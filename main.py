from PyQt5 import uic, QtCore
import matplotlib
matplotlib.use('Qt5Agg')
import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

# import hardware classes
from cameras import Dummy as Cam
from stages import Dummy as Stage

Ui_MainWindow, QMainWindow = uic.loadUiType("MainWindow.ui")

class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, facecolor=(0.1960, 0.1960, 0.1960))
        self.axes = fig.add_subplot(111)
        self.axes.set_xlabel("Wavelength /nm (uncalibrated)")
        self.axes.set_ylabel("Intensity")
        self.axes.grid('true', axis='x')
        self.axesR = self.axes.twinx()
        self.axesR.set_ylabel("difference signal (mOD)")
        self.axesR.grid('true')
        fig.tight_layout()
        super(MplCanvas, self).__init__(fig)


class MplCanvas_2d(FigureCanvas):

    def __init__(self, parent=None, width=6, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor=(0.1960, 0.1960, 0.1960))
        self.axes = self.fig.add_subplot(111)
        self.axes.set_xlabel("Wavelength /nm (uncalibrated)")
        self.axes.set_ylabel("Step #")
        self.fig.tight_layout()
        super(MplCanvas_2d, self).__init__(self.fig)


class Main(QMainWindow, Ui_MainWindow):

    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)
        self.showMaximized()

        matplotlib.rcParams['xtick.color'] = 'w'
        matplotlib.rcParams['ytick.color'] = 'w'
        matplotlib.rcParams['text.color'] = 'w'
        matplotlib.rcParams['axes.labelcolor'] = 'w'
        matplotlib.rcParams['axes.labelweight'] = 'bold'
        #matplotlib.rcParams['axes.grid'] = 'false'
        matplotlib.rcParams['grid.linestyle'] = ':'
        matplotlib.rcParams['axes.xmargin'] = '0'
        matplotlib.rcParams['axes.autolimit_mode'] = 'data'

        # load camera class
        self.cam = Cam()
        # load stage class
        self.stage = Stage()

        # get wavelength as x-axis
        self.xdata = self.cam.generate_wavelength_axis()
        
        # create the mpl canvas
        self.canvas = MplCanvas(self, width=6, height=5, dpi=100)
        # and add it to the vertical layout called mplvl
        self.mplvl.addWidget(self.canvas)
        # create plot reference
        self._plot_ref = None


        self.canvas2d = MplCanvas_2d(self, width=6, height=5, dpi=100)
        self.mplvl2d.addWidget(self.canvas2d)
        self._plot2d_ref = None
        
        # init plot(s)
        self.get_single()

        # connect buttons
        self.btn_getSingleAcq.clicked.connect(self.get_single)
        self.btn_contAcq.clicked.connect(self.continuous_acquisition)
        self.sldr_diffScale.valueChanged.connect(self.rescale)

    def get_single(self):
        # get a single camera acquisition
        #self.ydata = self.cam.single_acquisition()
        # or...
        #self.cam.single_acquisition()
        #self.ydata = self.cam.cam1
        # or...
        self.cam1, self.cam2, self.ydata = self.cam.single_acquisition()
        self.update_plot()
        self.update_plot_2d()

    def update_plot(self):
        
        # plot in case it doesn't exist yet
        if self._plot_ref is None:
            plot_refs = self.canvas.axes.plot(self.xdata,self.cam1,'r')
            self._plot_ref = plot_refs[0]
            plot_refs = self.canvas.axes.plot(self.xdata,self.cam2,'b')
            self._plot_ref2 = plot_refs[0]
            plot_refs = self.canvas.axesR.plot(self.xdata,self.ydata,'gray')
            self._plot_refR = plot_refs[0]
            self.canvas.axesR.fill_between(self.xdata, 0, self.ydata, where=np.array(self.ydata)>0, facecolor='red', interpolate=True, alpha=0.25)
            self.canvas.axesR.fill_between(self.xdata, 0, self.ydata, where=np.array(self.ydata)<0, facecolor='blue', interpolate=True, alpha=0.25)
            #self.canvas.axesR.hlines(0, self.xdata[0], self.xdata[-1],'k')
            self.canvas.axesR.plot(self.xdata,[0*i for i in self.xdata],'gray')
            
        # update data otherwise
        else:
            self._plot_ref.set_ydata(self.cam1)
            self._plot_ref2.set_ydata(self.cam2)
            self._plot_refR.set_ydata(self.ydata)
            #self.path.vertices[:, 1] = self.ydata
            self.canvas.axesR.collections.clear()
            self.canvas.axesR.fill_between(self.xdata, 0, self.ydata, where=np.array(self.ydata)>0, facecolor='red', interpolate=True, alpha=0.25)
            self.canvas.axesR.fill_between(self.xdata, 0, self.ydata, where=np.array(self.ydata)<0, facecolor='blue', interpolate=True, alpha=0.25)

        self.canvas.draw()
        

    def update_plot_2d(self):

        if self._plot2d_ref is None:
            step_range = 50
            xx, yy = np.meshgrid(np.linspace(min(self.xdata), max(self.xdata), self.cam.pixel),
                                 np.arange(0, step_range, 1))
            self.ydata2d = np.zeros((step_range, self.cam.pixel))
            self.ydata2d[-1, :] = self.ydata

            self.plot2d = self.canvas2d.axes.pcolormesh(xx, yy, self.ydata2d,shading='auto',cmap='coolwarm')
            #cMap = ListedColormap(['blue', 'purple', 'white', 'yellow', 'red'])
            self.canvas2d.fig.colorbar(self.plot2d, fraction=0.05, pad=0.03, label='difference signal (mOD)')
            self.plot2d.set_clim(-2,2)
            self._plot2d_ref = 1
        else:
            self.ydata2d = np.roll(self.ydata2d, -1, axis=0)
            self.ydata2d[-1,:] = self.ydata
            self.plot2d.set_array(np.ravel(self.ydata2d))

        self.canvas2d.draw()

    def rescale(self):
        val = self.sldr_diffScale.value() / 100
        self.canvas.axesR.set_ylim((-val,val))
        self.plot2d.set_clim(-val,val)
        if self.btn_contAcq.isChecked():
            pass
        else:
            self.update_plot()
            self.update_plot_2d()

    def continuous_acquisition(self):
        # check button state and execute accordingly
        if self.btn_contAcq.isChecked():
            self.timer = QtCore.QTimer()
            self.timer.setInterval(250)
            self.timer.timeout.connect(self.get_single)
            self.timer.start()
        else:
            self.timer.stop()

# define main
def main():
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    

    main()
