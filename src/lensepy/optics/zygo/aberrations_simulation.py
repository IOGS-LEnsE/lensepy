from lensepy.optics.zygo import *
import numpy as np
from matplotlib import pyplot as plt

class SimulatedPhase:

    def __init__(self, nb_steps=256, pixel_size=1e-6):
        self.coefficients = []
        self.nb_steps = nb_steps
        self.pixel_size = pixel_size
        self.wavelength = 632.8e-9 # HeNe
        self.simulated_surface = None
        self.complex_pupil = None
        self.perfect_psf = None
        self.psf_real = None

        # Generate area with circular mask
        R = 1
        y, x = np.indices((self.nb_steps, self.nb_steps))
        x = (x - self.nb_steps / 2) / (self.nb_steps / 2)
        y = (y - self.nb_steps / 2) / (self.nb_steps / 2)
        x_phys = x * self.pixel_size
        y_phys = y * self.pixel_size
        # Generate pupil
        self.r = np.sqrt(x ** 2 + y ** 2)
        self.theta = np.arctan2(y, x)
        self.pupil = (self.r <= R)

    def set_coefficients(self, coeffs):
        self.coefficients = coeffs

    def get_complex_pupil(self):
        """

        """
        if self.simulated_surface is None:
            raise ValueError("Surface simulée non définie. Appeler process_surface() avant.")
            return None, 0

        # Pupil complexe
        self.complex_pupil = np.zeros_like(self.simulated_surface, dtype=complex)
        self.complex_pupil[self.pupil] = np.exp(1j * self.simulated_surface[self.pupil])
        self.complex_pupil = np.ma.masked_where(np.logical_not(self.pupil), self.complex_pupil)

        return self.complex_pupil, self.complex_pupil.shape[0]

    def process_surface(self):
        Z = []

        for j in range(1, len(self.coefficients)):
            Zj = Zernike.get_coefficients_polar(j, self.r, self.theta)
            Zj[~self.pupil] = 0
            Z.append(Zj)

        # Phase reconstruction
        W_rec = np.zeros_like(self.pupil, dtype=float)
        for a, Zj in zip(self.coefficients, Z):
            W_rec += a * Zj
        W_rec[~self.pupil] = np.nan
        self.simulated_surface = np.ma.masked_where(np.logical_not(self.pupil), W_rec)
        return self.simulated_surface, self.pupil

    def get_psf(self, pad_factor=8, normalized=True):
        N = self.complex_pupil.shape[0]
        center = pad_factor * N // 2
        half_width = N // 2
        if self.perfect_psf is None:
            perfect_phase = np.zeros((N, N), dtype=float)
            perfect_complex_pupil = np.zeros_like(self.simulated_surface, dtype=complex)
            perfect_complex_pupil[self.pupil] = np.exp(1j * perfect_phase[self.pupil])
            U_padded_perfect = np.zeros((pad_factor * N, pad_factor * N), dtype=complex)
            U_padded_perfect[N // 2:N // 2 + N, N // 2:N // 2 + N] = perfect_complex_pupil
            self.perfect_psf = np.abs(np.fft.fftshift(np.fft.fft2(U_padded_perfect))) ** 2
            # Centering
            self.perfect_psf = self.perfect_psf[
                center - half_width:center + half_width, center - half_width:center + half_width]
            if normalized:
                self.perfect_psf /= self.perfect_psf.max()
        if self.complex_pupil is not None:
            U_padded = np.zeros((pad_factor * N, pad_factor * N), dtype=complex)
            U_padded[N // 2:N // 2 + N, N // 2:N // 2 + N] = self.complex_pupil
            self.psf_real = np.abs(np.fft.fftshift(np.fft.fft2(U_padded))) ** 2
            '''
            fft_field = np.fft.fftshift(np.fft.fft2(np.fft.fftshift(self.complex_pupil)))
            psf = np.abs(fft_field) ** 2
            psf /= psf.max()
            '''
            # Centering
            self.psf_real = self.psf_real[
                center - half_width:center + half_width, center - half_width:center + half_width]
            if normalized:
                self.psf_real /= self.psf_real.max()

            return self.psf_real, self.perfect_psf
        return None, None



if __name__ == "__main__":
    s_phase = SimulatedPhase()
    coeffs = [0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0]

    '''
    s_phase.set_coefficients(coeffs)
    surface, mask = s_phase.process_surface()
    c_pupil, N = s_phase.get_complex_pupil()

    psf_c, psf_perfect = s_phase.get_psf()
    plt.figure()
    plt.imshow(surface)
    plt.colorbar()
    plt.title("Phase (linéaire)")
    plt.figure()
    plt.imshow(np.angle(c_pupil))
    plt.colorbar()
    plt.title("Phase (linéaire)")

    plt.figure()
    plt.imshow(np.abs(psf_perfect))
    plt.colorbar()
    plt.title("PSF - Airy")
    plt.figure()
    plt.imshow(np.abs(psf_c))
    plt.colorbar()
    plt.title("PSF - Surface")
    '''
    psf_c_l = []
    plt.figure()
    for k in [1, 2, 5, 10]:
        coeffs2 = [x * k for x in coeffs]
        s_phase.set_coefficients(coeffs2)
        surface, mask = s_phase.process_surface()
        c_pupil, N = s_phase.get_complex_pupil()
        psf_c, psf_perfect = s_phase.get_psf(normalized=False)
        plt.plot(psf_c[N//2, :], label=f'k = {k}')

    plt.plot(psf_perfect[N//2, :], label=f'perfect', linestyle='--')
    plt.legend()


    plt.figure()
    plt.imshow(np.abs(psf_c))
    plt.colorbar()
    plt.title("PSF - Surface")

    plt.show()
