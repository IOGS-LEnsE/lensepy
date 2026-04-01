# -*- coding: utf-8 -*-
"""*psf.py* file.

./models/psf.py contains PSFModel class to process the Point Spread Function of a wavefront.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
Creation : april/2025
"""
import numpy as np

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lensepy.optics.zygo.phase import PhaseModel

def process_statistics_surface(surface):
    # Process (Peak-to-Valley) and RMS
    PV = np.round(np.nanmax(surface) - np.nanmin(surface), 2)
    RMS = np.round(np.nanstd(surface), 2)
    return PV, RMS

class PSFModel:
    """Class to process the Point Spread Function of a wavefront
    """
    def __init__(self, phase: "PhaseModel"=None, wavefront=None, mask=None):
        """

        """
        self.phase: "PhaseModel" = phase
        self.perfect_psf = None
        self.psf_real = None

        if self.phase is not None:
            self.wavefront = self.phase.get_unwrapped_phase()
            self.mask = self.phase.get_mask()
        else:
            self.wavefront = wavefront
            self.mask = mask

        self.complex_pupil = np.zeros_like(self.wavefront, dtype=complex)
        self.complex_pupil[self.mask] = np.exp(1j * self.wavefront[self.mask])
        self.complex_pupil = np.ma.masked_where(np.logical_not(self.mask), self.complex_pupil)


    def get_psf(self, pad_factor=8, normalized=True):
        if self.complex_pupil is None:
            print("Get COMPLEX Pupil")
            self.get_pupil()
        N = self.complex_pupil.shape[0]
        center = pad_factor * N // 2
        half_width = N // 2
        if self.perfect_psf is None:
            perfect_phase = np.zeros((N, N), dtype=float)
            perfect_complex_pupil = np.zeros_like(self.complex_pupil, dtype=complex)
            perfect_complex_pupil[self.mask] = np.exp(1j * perfect_phase[self.mask])
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

    def get_ftm(self, normalized=True):
        ftm_perfect = None
        if self.psf_real is not None:
            OTF = np.fft.fftshift(np.fft.fft2(self.psf_real))
            ftm = np.abs(OTF)
            if normalized:
                ftm /= ftm.max()
            if self.perfect_psf is not None:
                OTF_perfect = np.fft.fftshift(np.fft.fft2(self.perfect_psf))
                ftm_perfect = np.abs(OTF_perfect)
                if normalized:
                    ftm_perfect /= ftm_perfect.max()
            return ftm, ftm_perfect
        else:
            return None, None

    def get_wavefront(self):
        return self.wavefront

    def get_pupil(self):
        return self.complex_pupil

    def get_psf_real(self):
        return self.psf_real

    def get_mask(self):
        return self.mask



if __name__ == '__main__':
    import sys, os
    from matplotlib import pyplot as plt
    from lensepy.optics.zygo.dataset import DataSet
    from lensepy.optics.zygo.phase import PhaseModel
    from lensepy.optics.zygo.aberrations_simulation import SimulatedPhase

    coeffs = [0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0]

    '''
    nb_of_images_per_set = 5
    file_path = './_data/test3.mat'
    data_set = DataSet()
    data_set.load_images_set_from_file(file_path)
    data_set.load_masks_from_file(file_path)

    phase_test = PhaseModel(data_set)
    '''

    phase_test = SimulatedPhase()
    phase_test.set_coefficients(coeffs)

    ## Test class
    phase_test.prepare_data(coeffs)
    '''
    if phase_test.process_wrapped_phase():
        print('Wrapped Phase OK')
    wrapped = phase_test.get_wrapped_phase()
    if wrapped is not None:
        plt.figure()
        plt.imshow(wrapped.T, cmap='gray')
    '''
    if phase_test.process_unwrapped_phase():
        print('Unwrapped Phase OK')
    unwrapped = phase_test.get_unwrapped_phase()
    if unwrapped is not None:
        plt.figure()
        plt.imshow(unwrapped, cmap='gray')
        plt.colorbar()

    # Test class
    psf = PSFModel(phase_test)
    psf_disp, psf_perfect = psf.get_psf(normalized=False)
    wf = psf.get_wavefront()

    pup = psf.get_pupil()
    plt.figure()
    plt.imshow(np.abs(pup), cmap='gray')
    plt.colorbar()

    plt.figure()
    plt.imshow(psf_disp, cmap='gray')
    plt.colorbar()
    plt.figure()
    plt.imshow(psf_perfect, cmap='gray')
    plt.colorbar()

    psf_slice = psf_disp[psf_disp.shape[1]//2, :]

    plt.figure()
    plt.plot(psf_slice)

    plt.show()