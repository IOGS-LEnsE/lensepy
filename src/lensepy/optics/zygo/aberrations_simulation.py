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
        self.r = None       # polar coordonates
        self.theta = None   #
        self.pupil = None   # Mask

        # Generate area with circular mask
        self.R = 1
        self.set_pupil_radius(self.R)

    def set_pupil_radius(self, value):
        """
        :param value: float from 0 to 1.
        """
        self.R = value
        y, x = np.indices((self.nb_steps, self.nb_steps))
        x = (x - self.nb_steps / 2) / (self.nb_steps / 2)
        y = (y - self.nb_steps / 2) / (self.nb_steps / 2)
        x_phys = x * self.pixel_size
        y_phys = y * self.pixel_size
        # Generate pupil
        self.r = np.sqrt(x ** 2 + y ** 2)
        self.theta = np.arctan2(y, x)
        self.pupil = (self.r <= self.R)

    def set_coefficients(self, coeffs):
        self.coefficients = coeffs

    def prepare_data(self, coeffs):
        self.set_coefficients(coeffs)
        self.process_unwrapped_phase()

    def get_complex_pupil(self):
        """

        """
        if self.simulated_surface is None:
            self.process_unwrapped_phase()
            '''
            raise ValueError("Surface simulée non définie. Appeler process_unwrapped_phase() avant.")
            return None, 0
            '''

        # Pupil complexe
        self.complex_pupil = np.zeros_like(self.simulated_surface, dtype=complex)
        self.complex_pupil[self.pupil] = np.exp(1j * self.simulated_surface[self.pupil])
        self.complex_pupil = np.ma.masked_where(np.logical_not(self.pupil), self.complex_pupil)

        return self.complex_pupil, self.complex_pupil.shape[0]

    def get_surface(self):
        """

        :return: 2D surface, size of the surface (square)
        """
        return self.simulated_surface, self.simulated_surface.shape[0]

    def process_unwrapped_phase(self):
        Z = []

        for j in range(1, len(self.coefficients)):
            Zj = Zernike.get_coefficients_polar(j, self.r/self.R, self.theta)
            Zj[~self.pupil] = 0
            Z.append(Zj)

        # Phase reconstruction
        W_rec = np.zeros_like(self.pupil, dtype=float)
        for a, Zj in zip(self.coefficients, Z):
            W_rec += a * Zj
        W_rec[~self.pupil] = np.nan
        self.simulated_surface = np.ma.masked_where(np.logical_not(self.pupil), W_rec)
        return self.simulated_surface, self.pupil

    def get_unwrapped_phase(self):
        surface, pupil = self.process_unwrapped_phase()
        return surface

    '''
    def get_psf2(self, pad_factor=8, normalized=True):
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

            # Centering
            self.psf_real = self.psf_real[
                center - half_width:center + half_width, center - half_width:center + half_width]
            if normalized:
                self.psf_real /= self.psf_real.max()

            return self.psf_real, self.perfect_psf
        return None, None
    '''

    def get_mask(self):
        return self.pupil


#####################
"""
ZOOM SQUARE !!!
"""

def zoom_image_square(img, threshold=1e-3):
    """
    img : tableau numpy (H, W) ou (H, W, C)
    threshold : seuil en dessous duquel une valeur est considérée comme nulle
    """

    h, w = img.shape[:2]

    assert h == w, "L'image initiale doit être carrée"

    # Centre de l'image originale
    cx = w // 2
    cy = h // 2

    # Détection des valeurs significatives
    if img.ndim == 3:
        mask = np.max(np.abs(img), axis=2) > threshold
    else:
        mask = np.abs(img) > threshold

    y, x = np.where(mask)

    if len(x) == 0:
        return img

    # Distance maximale entre le centre de l'image
    # et la zone significative
    radius = max(
        np.max(np.abs(x - cx)),
        np.max(np.abs(y - cy))
    )

    # Pour avoir un crop carré centré exactement sur (cx, cy)
    x0 = cx - radius
    x1 = cx + radius
    y0 = cy - radius
    y1 = cy + radius

    # Sécurité
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(w, x1)
    y1 = min(h, y1)

    return img[y0:y1, x0:x1], radius

def crop_square_radius(img, radius):
    """
    Croppe une image carrée autour de son centre.

    Parameters
    ----------
    img : np.ndarray
        Image carrée, de forme (H, W) ou (H, W, C).
    radius : int
        Rayon du crop en pixels.

    Returns
    -------
    np.ndarray
        Image cropée de taille approximative (2*radius, 2*radius).
    """
    h, w = img.shape[:2]

    if h != w:
        raise ValueError("L'image doit être carrée.")

    if radius <= 0:
        raise ValueError("Le radius doit être strictement positif.")

    cx = w // 2
    cy = h // 2

    x_min = cx - radius
    x_max = cx + radius
    y_min = cy - radius
    y_max = cy + radius

    # Vérification que le crop reste dans l'image
    if x_min < 0 or y_min < 0 or x_max > w or y_max > h:
        raise ValueError(
            f"Radius trop grand. Maximum possible : {min(cx, cy)} pixels."
        )

    return img[y_min:y_max, x_min:x_max]



if __name__ == "__main__":

    s_phase = SimulatedPhase()
    coeffs = [0, 0, 0, -0.5, 0, 0, 0.5, 0, 0.2, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0]

    s_phase.set_coefficients(coeffs)
    s_phase.set_pupil_radius(0.5)
    surface, mask = s_phase.process_unwrapped_phase()
    c_pupil, N = s_phase.get_complex_pupil()

    psf = PSFModel(s_phase)
    psf_c, psf_perfect, center_x, padding = psf.get_psf(normalized=True)

    ftm_c, ftm_perfect = psf.get_ftm(normalized=True)

    strehl_ratio = psf.get_strehl_ratio()
    line_slice = center_x//padding

    # Display all
    fig, ax = plt.subplots(nrows=2, ncols=3)
    # Plot data in each subplot
    im00 = ax[0,0].imshow(surface)
    ax[0,0].set_title('Phase of the surface')
    fig.colorbar(im00, ax=ax[0,0])
    im01 = ax[0,1].imshow(strehl_ratio*np.abs(psf_c))
    ax[0,1].set_title(f'PSF of the surface - Strehl = {np.round(strehl_ratio, 3)}')
    fig.colorbar(im01, ax=ax[0,1])
    im02 = ax[0,2].imshow(np.abs(ftm_c))
    ax[0,1].set_title(f'PSF of the surface - Strehl = {np.round(strehl_ratio, 3)}')
    fig.colorbar(im02, ax=ax[0,2])

    ax[1,0].imshow(np.abs(psf_perfect))
    ax[1,0].set_title('Airy')
    ax[1,1].plot(strehl_ratio*psf_c[line_slice,:], label='Real PSF')
    ax[1,1].plot(psf_perfect[:,line_slice], label='Perfect PSF (Airy)')
    ax[1,1].legend()
    ax[1,1].set_title('Slice of each PSF')
    ax[1,2].plot(strehl_ratio*ftm_c[line_slice,line_slice:int(1.2*line_slice)], label='Real FTM')
    ax[1,2].plot(ftm_perfect[line_slice:int(1.2*line_slice),line_slice], label='Perfect FTM (Airy)')
    ax[1,2].legend()
    ax[1,2].set_title('Slice of each FTM')

    plt.show()