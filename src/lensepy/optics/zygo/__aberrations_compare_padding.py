from aberrations_simulation import *
import timeit

N_REPET = 1

def get_psf_frequency_axis(N_size, pad_factor, dx):
    N_fft = pad_factor * N_size

    freq = np.fft.fftshift(
        np.fft.fftfreq(N_fft, d=dx)
    )

    center = N_fft // 2
    half = N_size // 2

    freq_crop = freq[center-half:center+half]

    return freq_crop

if __name__ == "__main__":

    threshold_zoom = 0.01

    s_phase = SimulatedPhase(nb_steps=128)
    coeffs = [0, 0, 0, -0.5, 0, 0, 0.5, 0, 0.2, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0]

    s_phase.set_coefficients(coeffs)
    s_phase.set_pupil_radius(1)
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
    ax[1,2].plot(strehl_ratio*ftm_c[line_slice,line_slice:int(line_slice*1.25)], label='Real FTM')
    ax[1,2].plot(ftm_perfect[line_slice:int(line_slice*1.25),line_slice], label='Perfect FTM (Airy)')
    ax[1,2].legend()
    ax[1,2].set_title('Slice of each FTM')


    # EFFECT OF PADDING
    padding_zoom = [2, 4, 8, 16, 32]

    plt.figure()
    for k, pad_z in enumerate(padding_zoom):
        temps = timeit.timeit(
            lambda: psf.get_psf(normalized=True, restart=True, pad_factor=pad_z),
            number=N_REPET
        )
        psf_c, psf_perfect, center_x, padding = psf.get_psf(normalized=True, restart=True, pad_factor=pad_z)
        line_slice = center_x // padding
        freq = get_psf_frequency_axis(psf_c.shape[0], padding, 1)
        print(f'Freq shape = {freq.shape}')
        print(f'Shape = {psf_perfect.shape} / Pad = {padding} / Center = {center_x} /  Slice = {line_slice} / Temps = {temps/10:.2f}')
        #plt.plot(strehl_ratio*psf_c[line_slice,:], label=f'Real PSF - Pad = {pad_z}')
        plt.plot(freq, psf_perfect[:,line_slice] + k*0.1, label=f'Perfect PSF (Airy) - Pad = {pad_z} / T = {temps/10:.2f}')
        plt.legend()



    plt.show()