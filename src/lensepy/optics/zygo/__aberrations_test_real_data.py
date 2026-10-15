from aberrations_simulation import *
#from colour.examples.phenomena.examples_rayleigh import wavelength

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
    psf_c_init, psf_perfect_init, center_x, padding = psf.get_psf(normalized=True)

    ftm_c, ftm_perfect = psf.get_ftm(normalized=True)

    strehl_ratio = psf.get_strehl_ratio()
    line_slice = center_x//padding

    # Zoom
    psf_c, size_z = zoom_image_square(psf_c_init, threshold=threshold_zoom)
    line_slice_psf = psf_c.shape[0] // 2
    #line_slice_psf = psf_c_init.shape[0] // 2  # No zoom
    psf_perfect = crop_square_radius(psf_perfect_init, size_z)

    # AXIS

    ''' From matlab / PSFZygo.m
    Ne = 512;
    %choix du zoom_psf
    %1 : Ne = 512 N_Phi 256
    %2 : Ne = 512 N_Phi 128
    N_Phi= Ne/(2^zoom_psf);
    Rapport_pupille_plan=Ne/N_Phi; %taille du cadre sur taille de la pupille
    Lambda = 632.8*1E-6 %en mm
    Rayon_image=Lambda*N_ouverture;
    x_image = 1e3 * (Rayon_image / Rapport_pupille_plan) * (-Ne / 2:+Ne / 2-1); %axe
    de
    l'image echelle en microns
    '''
    N_size = psf_c_init.shape[0]
    N = psf_c.shape[0]
    wavelength = 632.8*1E-9
    f_number = 4
    ratio_pupil = 0.5
    image_radius = wavelength * f_number * ratio_pupil
    x_ax_surface = np.linspace(-N_size//2, N_size//2-1, N_size) * image_radius * 1e3    # mm
    # With zoom
    borne_x1 = (N_size - N) // 2
    borne_x2 = borne_x1 + N
    print(f'N = {N} - N_size = {N_size} // BX1 = {borne_x1} / BX2 = {borne_x2}')

    df = 1
    f = (np.arange(N) - N // 2) * df
    # Diagonale principale : haut-gauche -> bas-droite
    diag_ftm_tl_br = np.diag(ftm_c)
    # Diagonale secondaire : haut-droite -> bas-gauche
    diag_ftm_tr_bl = np.diag(np.fliplr(ftm_c))
    f_diag = f * np.sqrt(2)


    # Display all
    fig, ax = plt.subplots(nrows=2, ncols=3)
    # Plot data in each subplot
    im00 = ax[0,0].imshow(surface)
    ax[0,0].set_title('Phase of the surface')
    fig.colorbar(im00, ax=ax[0,0])
    im01 = ax[0,1].imshow(strehl_ratio*np.abs(psf_c),
                          extent=[x_ax_surface[borne_x1], x_ax_surface[borne_x2],
                          x_ax_surface[borne_x1], x_ax_surface[borne_x2]])
    ax[0,1].set_title(f'PSF of the surface - Strehl = {np.round(strehl_ratio, 3)}')
    fig.colorbar(im01, ax=ax[0,1])
    im02 = ax[0,2].imshow(np.abs(ftm_c))
    ax[0,1].set_title(f'PSF of the surface - Strehl = {np.round(strehl_ratio, 3)}')
    fig.colorbar(im02, ax=ax[0,2])


    ax[1,0].imshow(np.abs(psf_perfect), extent=[x_ax_surface[borne_x1], x_ax_surface[borne_x2],
                                            x_ax_surface[borne_x1], x_ax_surface[borne_x2]])
    ax[1,0].set_title('PSF (Airy)')
    ax[1,1].plot(x_ax_surface[borne_x1:borne_x2], strehl_ratio*psf_c[line_slice_psf,:],
                 label='Real PSF')
    ax[1,1].plot(x_ax_surface[borne_x1:borne_x2], psf_perfect[:,line_slice_psf],
                 label='Perfect PSF (Airy)')
    ax[1,1].set_xlabel('in mm')
    ax[1,1].legend()
    ax[1,0].set_title('PSF')
    '''
    ax[1,2].plot(f[line_slice:], ftm_c[line_slice,line_slice:],
                 label='Real FTM')
    ax[1,2].plot(f[line_slice:], ftm_perfect[line_slice:,line_slice],
                 label='Perfect FTM (Airy)')
    ax[1,2].plot(f_diag[line_slice:], diag_ftm_tl_br[line_slice:],
                 label='Real FTM Diag')
    ax[1,2].legend()
    ax[1,2].set_title('Slice of each FTM')
    '''
    '''


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

    N = ftm_c.shape[0]
    df = 1
    f = (np.arange(N) - N // 2) * df
    # Diagonale principale : haut-gauche -> bas-droite
    diag_ftm_tl_br = np.diag(ftm_c)
    # Diagonale secondaire : haut-droite -> bas-gauche
    diag_ftm_tr_bl = np.diag(np.fliplr(ftm_c))
    f_diag = f * np.sqrt(2)

    ax[1,0].imshow(np.abs(psf_perfect))
    ax[1,0].set_title('Airy')
    ax[1,1].plot(strehl_ratio*psf_c[line_slice_psf,:], label='Real PSF')
    ax[1,1].plot(psf_perfect[:,line_slice_psf], label='Perfect PSF (Airy)')
    ax[1,1].legend()
    ax[1,1].set_title('Slice of each PSF')
    ax[1,2].plot(f[line_slice:], ftm_c[line_slice,line_slice:],
                 label='Real FTM')
    ax[1,2].plot(f[line_slice:], ftm_perfect[line_slice:,line_slice],
                 label='Perfect FTM (Airy)')
    ax[1,2].plot(f_diag[line_slice:], diag_ftm_tl_br[line_slice:],
                 label='Real FTM Diag')
    ax[1,2].legend()
    ax[1,2].set_title('Slice of each FTM')
    '''

    plt.show()