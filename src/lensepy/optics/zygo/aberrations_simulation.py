from lensepy.optics.zygo import *
import numpy as np
from matplotlib import pyplot as plt

class SimulatedPhase:

    def __init__(self, nb_steps=1000, pixel_size=1e-6):
        self.coefficients = []
        self.nb_steps = nb_steps
        self.pixel_size = pixel_size
        self.simulated_surface = None

        # Generate area with circular mask
        y, x = np.indices((self.nb_steps, self.nb_steps))
        x = (x - self.nb_steps / 2) / (self.nb_steps / 2)
        y = (y - self.nb_steps / 2) / (self.nb_steps / 2)
        x_phys = x * self.pixel_size
        y_phys = y * self.pixel_size
        # Generate pupil
        self.r = np.sqrt(x ** 2 + y ** 2)
        self.theta = np.arctan2(y, x)
        self.pupil = ~(self.r <= 1)

    def set_coefficients(self, coeffs):
        self.coefficients = coeffs

    def process_surface(self):
        Z = []

        for j in range(1, len(self.coefficients) + 1):
            Zj = Zernike.get_coefficients_polar(j, self.r, self.theta)
            Zj[self.pupil] = 0
            Z.append(Zj)

        # Phase reconstruction
        W_rec = np.zeros_like(self.pupil, dtype=float)
        for a, Zj in zip(self.coefficients, Z):
            W_rec += a * Zj
        W_rec[self.pupil] = 0
        self.simulated_surface = np.ma.array(W_rec, mask=self.pupil)
        return self.simulated_surface


if __name__ == "__main__":
    s_phase = SimulatedPhase()
    coeffs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 1]
    s_phase.set_coefficients(coeffs)
    surface = s_phase.process_surface()

    plt.figure()
    plt.imshow(surface)
    plt.colorbar()
    plt.show()