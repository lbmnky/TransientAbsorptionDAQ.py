import random, operator
import numpy as np

class Camera:
    
    def __init__(self):
        pass

    def single_acquisition(self):
        pass

    def generate_wavelength_axis(self):
        pass


class Dummy(Camera):
    
    def __init__(self):
        super().__init__()
        self.pixel = 1024

    def single_acquisition(self):
        cam1 = [10000 * np.exp(-(i-600)**2/500**2) + 5000 + random.randint(0, 20) for i in range(self.pixel)]
        cam2 = [10000 * np.exp(-(i-600)**2/500**2) + 5000 + random.randint(0, 20) for i in range(self.pixel)]
        sample_abs = [3500 * np.exp(-(i - 500)**2/200**2) + random.randint(0, 20) for i in range(self.pixel)]
        sample_abs_pumped = [3400 * np.exp(-(i - 510)**2/210**2) + random.randint(0, 20) for i in range(self.pixel)]

        cam1 = list(map(operator.sub,cam1,sample_abs))
        sample_ta = list(map(operator.sub,sample_abs,sample_abs_pumped))

        #diff = list(map(operator.truediv,(map(operator.sub, cam1, cam2)),cam1))
        diff = list(map(operator.truediv,sample_ta,cam1))
        return cam1, cam2, [i * 1000 for i in diff]
    def generate_wavelength_axis(self):
        return [0.5 * i + 350 for i in range(self.pixel)]
