from aberrations_simulation import *


if __name__ == "__main__":

    file_path = '../../../../../lensepy-data/optics/zygo/test4.mat'
    threshold_zoom = 0.01

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

    # Zoom
    psf_c, size_z = zoom_image_square(psf_c, threshold=threshold_zoom)
    line_slice_psf = psf_c.shape[0] // 2
    psf_perfect = crop_square_radius(psf_perfect, size_z)

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
    ax[1,1].plot(strehl_ratio*psf_c[line_slice_psf,:], label='Real PSF')
    ax[1,1].plot(psf_perfect[:,line_slice_psf], label='Perfect PSF (Airy)')
    ax[1,1].legend()
    ax[1,1].set_title('Slice of each PSF')
    ax[1,2].plot(strehl_ratio*ftm_c[line_slice,line_slice:], label='Real FTM')
    ax[1,2].plot(ftm_perfect[line_slice:,line_slice], label='Perfect FTM (Airy)')
    ax[1,2].legend()
    ax[1,2].set_title('Slice of each FTM')



    ########################
    # Test on real data
    #######################"
    from lensepy.optics.zygo.dataset import DataSet
    nb_of_images_per_set = 5
    data_set = DataSet()
    data_set.load_images_set_from_file(file_path)
    data_set.load_masks_from_file(file_path)

    phase_test = PhaseModel(data_set)
    phase_test.process_data()

    surface = phase_test.get_unwrapped_phase()
    mask = phase_test.get_mask()

    psf = PSFModel(wavefront=surface, mask=mask)
    psf_c, psf_perfect, center_x, padding = psf.get_psf(normalized=True)

    ftm_c, ftm_perfect = psf.get_ftm(normalized=True)

    strehl_ratio = psf.get_strehl_ratio()
    line_slice = center_x // padding

    # Zoom
    psf_c, size_z = zoom_image_square(psf_c, threshold=threshold_zoom)
    line_slice_psf = psf_c.shape[0] // 2
    psf_perfect = crop_square_radius(psf_perfect, size_z)

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
    ax[1,1].plot(strehl_ratio*psf_c[line_slice_psf,:], label='Real PSF')
    ax[1,1].plot(psf_perfect[:,line_slice_psf], label='Perfect PSF (Airy)')
    ax[1,1].legend()
    ax[1,1].set_title('Slice of each PSF')
    ax[1,2].plot(strehl_ratio*ftm_c[line_slice,line_slice:], label='Real FTM')
    ax[1,2].plot(ftm_perfect[line_slice:,line_slice], label='Perfect FTM (Airy)')
    ax[1,2].legend()
    ax[1,2].set_title('Slice of each FTM')

    plt.show()