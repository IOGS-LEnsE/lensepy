import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft2, ifft2, fftshift

# --- Paramètres ---
N = 256               # Taille de la pupille (pixels)
D = 1.0               # Diamètre normalisé de la pupille
f = 1.0               # Distance focale normalisée

# --- Création d'une grille de pupille ---
x = np.linspace(-1, 1, N)
y = np.linspace(-1, 1, N)
X, Y = np.meshgrid(x, y)
R = np.sqrt(X**2 + Y**2)

# --- Masque circulaire ---
pupil = R <= 1

# --- Exemple de phase : aberration sphérique ---
phi = 0.5 * R**4 * pupil  # en radians

# --- Champ complexe ---
A = pupil.astype(float)   # amplitude uniforme sur la pupille
U = A * np.exp(1j * phi)

# --- Réponse impulsionnelle ---
# Transformée de Fourier pour obtenir le PSF (point spread function)
PSF = fftshift(np.abs(fft2(U))**2)
PSF /= PSF.max()  # Normalisation

plt.figure(figsize=(6,5))
plt.imshow(PSF, extent=(-1,1,-1,1))
plt.title("Réponse impulsionnelle / PSF")
plt.colorbar(label="Intensité normalisée")
plt.show()

# --- Spot diagram ---
# Gradient de phase = direction des rayons
dx, dy = np.gradient(phi)
spot_x = f * dx[pupil]
spot_y = f * dy[pupil]

plt.figure(figsize=(5,5))
plt.scatter(spot_x, spot_y, s=1)
plt.title("Spot diagram")
plt.xlabel("x (plan image)")
plt.ylabel("y (plan image)")
plt.axis('equal')
plt.grid(True)
plt.show()