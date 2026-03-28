from lensepy.optics.zygo import *
import numpy as np
from matplotlib import pyplot as plt

class SimulatedPhase:

    def __init__(self, nb_steps=200, pixel_size=1e-6):
        self.coefficients = []
        self.nb_steps = nb_steps
        self.pixel_size = pixel_size
        self.wavelength = 632.8e-9 # HeNe
        self.simulated_surface = None
        self.complex_pupil = None

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

    def get_complex_pupil2(self):
        f_number = 1
        self.complex_pupil = np.zeros_like(self.simulated_surface, dtype=complex)
        self.complex_pupil[self.pupil] = np.exp(1j * self.simulated_surface[self.pupil])
        pixel_scale = self.wavelength * f_number  # m/pixel dans le plan focal
        N = self.complex_pupil.shape[0]
        x_psf = (np.arange(N) - N / 2) * self.pixel_size
        y_psf = (np.arange(N) - N / 2) * self.pixel_size
        return self.complex_pupil, x_psf, y_psf

    def get_complex_pupil(self, upsampling=2):
        """
        Retourne le pupil complexe avec padding léger pour augmenter la résolution de la PSF.
        upsampling : facteur pour augmenter la taille de la FFT
        """
        if self.simulated_surface is None:
            raise ValueError("Surface simulée non définie. Appeler process_surface() avant.")

        # Pupil complexe
        self.complex_pupil = np.zeros(self.simulated_surface.shape, dtype=complex)
        self.complex_pupil[self.pupil] = np.exp(1j * self.simulated_surface[self.pupil])

        # FFT avec padding léger pour améliorer la résolution de la PSF
        N = self.complex_pupil.shape[0]
        N_fft = N * upsampling  # facteur d’upsampling
        fft_field = np.fft.fftshift(
            np.fft.fft2(np.fft.fftshift(self.complex_pupil), s=(N_fft, N_fft))
        )

        # Axe spatial dans le plan focal
        f_number = 1  # par défaut
        pixel_scale = self.pixel_size / upsampling  # m/pixel après upsampling
        x_psf = (np.arange(N_fft) - N_fft / 2) * pixel_scale
        y_psf = (np.arange(N_fft) - N_fft / 2) * pixel_scale

        return self.complex_pupil, x_psf, y_psf, fft_field

    def process_surface(self):
        Z = []

        for j in range(1, len(self.coefficients) + 1):
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

    def get_psf(self):
        if self.complex_pupil is not None:
            fft_field = np.fft.fftshift(np.fft.fft2(np.fft.fftshift(self.complex_pupil)))
            psf = np.abs(fft_field) ** 2
            psf /= psf.max()
            return psf / psf.max()
        return None



### NEW TEST

## polar coordinates
def Zernike_polar(coefficients, r, u):
    Z = coefficients
    Z1  =  Z[0]  * 1*(np.cos(u)**2+np.sin(u)**2)
    Z2  =  Z[1]  * 2*r*np.cos(u)
    Z3  =  Z[2]  * 2*r*np.sin(u)
    Z4  =  Z[3]  * np.sqrt(3)*(2*r**2-1)
    Z5  =  Z[4]  * np.sqrt(6)*r**2*np.sin(2*u)
    Z6  =  Z[5]  * np.sqrt(6)*r**2*np.cos(2*u)
    Z7  =  Z[6]  * np.sqrt(8)*(3*r**2-2)*r*np.sin(u)
    Z8  =  Z[7]  * np.sqrt(8)*(3*r**2-2)*r*np.cos(u)
    '''
    Z9  =  Z[9]  * np.sqrt(8)*r**3*np.sin(3*u)
    Z10 =  Z[10] * np.sqrt(8)*r**3*np.cos(3*u)
    Z11 =  Z[11] * np.sqrt(5)*(1-6*r**2+6*r**4)
    Z12 =  Z[12] * np.sqrt(10)*(4*r**2-3)*r**2*np.cos(2*u)
    Z13 =  Z[13] * np.sqrt(10)*(4*r**2-3)*r**2*np.sin(2*u)
    Z14 =  Z[14] * np.sqrt(10)*r**4*np.cos(4*u)
    Z15 =  Z[15] * np.sqrt(10)*r**4*np.sin(4*u)
    Z16 =  Z[16] * np.sqrt(12)*(10*r**4-12*r**2+3)*r*np.cos(u)
    Z17 =  Z[17] * np.sqrt(12)*(10*r**4-12*r**2+3)*r*np.sin(u)
    Z18 =  Z[18] * np.sqrt(12)*(5*r**2-4)*r**3*np.cos(3*u)
    Z19 =  Z[19] * np.sqrt(12)*(5*r**2-4)*r**3*np.sin(3*u)
    Z20 =  Z[20] * np.sqrt(12)*r**5*np.cos(5*u)
    Z21 =  Z[21] * np.sqrt(12)*r**5*np.sin(5*u)
    Z22 =  Z[22] * np.sqrt(7)*(20*r**6-30*r**4+12*r**2-1)
    Z23 =  Z[23] * np.sqrt(14)*(15*r**4-20*r**2+6)*r**2*np.sin(2*u)
    Z24 =  Z[24] * np.sqrt(14)*(15*r**4-20*r**2+6)*r**2*np.cos(2*u)
    Z25 =  Z[25] * np.sqrt(14)*(6*r**2-5)*r**4*np.sin(4*u)
    Z26 =  Z[26] * np.sqrt(14)*(6*r**2-5)*r**4*np.cos(4*u)
    Z27 =  Z[27] * np.sqrt(14)*r**6*np.sin(6*u)
    Z28 =  Z[28] * np.sqrt(14)*r**6*np.cos(6*u)
    Z29 =  Z[29] * 4*(35*r**6-60*r**4+30*r**2-4)*r*np.sin(u)
    Z30 =  Z[30] * 4*(35*r**6-60*r**4+30*r**2-4)*r*np.cos(u)
    Z31 =  Z[31] * 4*(21*r**4-30*r**2+10)*r**3*np.sin(3*u)
    Z32 =  Z[32] * 4*(21*r**4-30*r**2+10)*r**3*np.cos(3*u)
    Z33 =  Z[33] * 4*(7*r**2-6)*r**5*np.sin(5*u)
    Z34 =  Z[34] * 4*(7*r**2-6)*r**5*np.cos(5*u)
    Z35 =  Z[35] * 4*r**7*np.sin(7*u)
    Z36 =  Z[36] * 4*r**7*np.cos(7*u)
    Z37 =  Z[37] * 3*(70*r**8-140*r**6+90*r**4-20*r**2+1)
    '''
    ZW = Z1 + Z2 +  Z3+  Z4+  Z5+  Z6+  Z7+  Z8#+  Z9+ Z10+ Z11+ Z12+ Z13+ Z14+ Z15+ Z16+ Z17+ Z18+ Z19+Z20+ Z21+ Z22+ Z23+ Z24+ Z25+ Z26+ Z27+ Z28+ Z29+Z30+ Z31+ Z32+ Z33+ Z34+ Z35+ Z36+ Z37
    return ZW

def pupil_size(D,lam,pix,size):
    pixrad = pix*np.pi/(180*3600)  # Pixel-size in radians
    nu_cutoff = D/lam      # Cutoff frequency in rad^-1
    deltanu = 1./(size*pixrad)     # Sampling interval in rad^-1
    rpupil = nu_cutoff/(2*deltanu) #pupil size in pixels
    return int(rpupil)

def phase(coefficients, rpupil):
    r = 1
    x = np.linspace(-r, r, 2 * rpupil)
    y = np.linspace(-r, r, 2 * rpupil)

    [X, Y] = np.meshgrid(x, y)
    R = np.sqrt(X ** 2 + Y ** 2)
    theta = np.arctan2(Y, X)

    Z = Zernike_polar(coefficients, R, theta)
    Z[R > 1] = 0
    return Z

def center(coefficients,size,rpupil):
    A = np.zeros([size,size])
    A[size//2-rpupil+1:size//2+rpupil+1,size//2-rpupil+1:size//2+rpupil+1]= phase(coefficients,rpupil)
    return A

def mask(rpupil, size):
    r = 1
    x = np.linspace(-r, r, 2*rpupil)
    y = np.linspace(-r, r, 2*rpupil)

    [X,Y] = np.meshgrid(x,y)
    R = np.sqrt(X**2+Y**2)
    theta = np.arctan2(Y, X)
    M = 1*(np.cos(theta)**2+np.sin(theta)**2)
    M[R>1] = 0
    Mask =  np.zeros([size,size])
    Mask[size//2-rpupil+1:size//2+rpupil+1,size//2-rpupil+1:size//2+rpupil+1]= M
    return Mask

def complex_pupil(A,Mask):
    abbe =  np.exp(1j*A)
    abbe_z = np.zeros((len(abbe),len(abbe)),dtype=complex)
    abbe_z = Mask*abbe
    return abbe_z

def PSF(complx_pupil):
    PSF = np.fft.ifftshift(np.fft.fft2(np.fft.fftshift(complx_pupil)))
    PSF = (np.abs(PSF))**2 #or PSF*PSF.conjugate()
    PSF = PSF/PSF.sum() #normalizing the PSF
    return PSF

def OTF(psf):
    otf = np.fft.ifftshift(psf) #move the central frequency to the corner
    otf = np.fft.fft2(otf)
    otf_max = float(otf[0,0]) #otf_max = otf[size/2,size/2] if max is shifted to center
    otf = otf/otf_max #normalize by the central frequency signal
    return otf

def MTF(otf):
    mtf = np.abs(otf)
    return mtf


if __name__ == "__main__":
    D = 140  # diameter of the aperture
    lam = 617.3 * 10 ** (-6)  # wavelength of observation
    pix = 0.5  # plate scale
    f = 4125.3  # effective focal length
    size = 500  # size of detector in pixels

    coeffs = [0, 0, 0, 0.8, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0]

    rpupil = pupil_size(D, lam, pix, size)
    sim_phase = center(coeffs, size, rpupil)
    Mask = mask(rpupil, size)

    plt.figure(figsize=(18, 10))
    plt.imshow(sim_phase)
    plt.colorbar()

    pupil_com = complex_pupil(sim_phase, Mask)

    psf = PSF(pupil_com)

    plt.figure(figsize=(18, 10))
    plt.imshow(np.abs(psf))
    plt.colorbar()

    otf = OTF(psf)
    mtf = MTF(otf)

    plt.figure(figsize=(18, 10))
    plt.imshow(np.fft.fftshift(mtf))
    plt.colorbar()

    '''
    s_phase = SimulatedPhase()
    coeffs = [0, 0, 0, 0.8, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0]
    s_phase.set_coefficients(coeffs)
    surface, mask = s_phase.process_surface()
    c_pupil, x_psf, y_psf, fft_field = s_phase.get_complex_pupil(upsampling=10)
    psf = np.abs(fft_field) ** 2
    psf /= psf.max()

    plt.figure()
    plt.imshow(psf, cmap='gray',
               extent=[x_psf.min() * 1e3, x_psf.max() * 1e3, y_psf.min() * 1e3, y_psf.max() * 1e3])
    plt.colorbar()
    plt.title("PSF (linéaire, plus nette)")

    plt.figure()
    plt.imshow(surface)
    plt.colorbar()
    plt.title("Phase (linéaire)")

    h = fft_field
    plt.imshow(np.abs(h), extent=[x_psf.min() * 1e3, x_psf.max() * 1e3, y_psf.min() * 1e3, y_psf.max() * 1e3])
    plt.title("Amplitude de la réponse impulsionnelle")
    plt.colorbar()
    '''
    plt.show()
