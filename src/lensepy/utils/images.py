import cv2
from matplotlib import pyplot as plt
import numpy as np

def resize_image_ratio(pixels: np.ndarray, new_height: int, new_width: int) -> np.ndarray:
    """Create a new array with a different size, with the same aspect ratio.

    :param pixels: Array of pixels to resize
    :type pixels: np.ndarray
    :param new_height: New height of the image.
    :type new_height: int
    :param new_width: New width of the image.
    :type new_width: int

    :return: A resized image.
    :rtype: np.ndarray
    """
    height, width = pixels.shape[:2]
    aspect_ratio = width / height

    # Calculate new size with same aspect_ratio
    n_width = new_width
    n_height = int(n_width / aspect_ratio)
    if n_height > new_height:
        n_height = new_height
        n_width = int(n_height * aspect_ratio)
    else:
        n_width = new_width
        n_height = int(n_width / aspect_ratio)
    resized_array = cv2.resize(pixels, (n_width, n_height))
    return resized_array

def imread_rgb(path: str):
    """
    Open an image from a file, after RGB conversion.
    :param path:    Path to image.
    :return:        np.ndarray RGB image.
    """
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    bits_depth = img.dtype.itemsize * 8
    if img is None:
        raise ValueError(f"Invalid path : {path}")
    if img.ndim == 2:
        # Déjà en gris → on garde tel quel
        return img, bits_depth
    if img.ndim == 3:
        if img.shape[2] == 3:
            # Conversion BGR → RGB
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB), 8
        elif img.shape[2] == 4:
            # Conversion BGRA → RGBA
            return cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA), 8
    return img, bits_depth


def process_hist_from_array(array: np.ndarray, bins: list, zoom: bool=False, bits_depth: int = 8) -> (np.ndarray, np.ndarray):
    """
    Calculate a histogram from an array and bins definition.
    :param array: Array containing data.
    :param bins: Bins to calculate the histogram.
    :param zoom: Zoom factor, True if zoom is activated.
    :param bits_depth: Number of bits depth.
    :return: Tuple of np.ndarray: bins and hist data.
    """
    max_val = 2**bits_depth-1
    # Grayscale image
    if array.ndim == 2:
        if zoom:
            vmin = np.min(array)
            vmax = np.max(array)
        else:
            vmin = 0
            vmax = max_val + 1
        hist_range = (vmin, vmax-1)
        nbins = int(vmax - vmin + 1)
        hist, bin_edges = np.histogram(array, bins=nbins, range=hist_range)
        return hist, bin_edges

    # RGB image
    elif array.ndim == 3 and array.shape[2] == 3:
        lum = 0.299 * array[:, :, 0] + 0.587 * array[:, :, 1] + 0.114 * array[:, :, 2]
        # RGB image
        if zoom:
            r_min, r_max = np.min(array[:, 0]), np.max(array[:, 0])
            g_min, g_max = np.min(array[:, 1]), np.max(array[:, 1])
            b_min, b_max = np.min(array[:, 2]), np.max(array[:, 2])
            l_min, l_max = np.min(lum), np.max(lum)
            vmin = np.min([r_min, g_min, b_min, l_min])
            vmax = np.max([r_max, g_max, b_max, l_max])
        else:
            vmin = 0
            vmax = max_val + 1

        hist_range = (vmin, vmax-1)
        nbins = int(vmax - vmin + 1)
        bin_edges = np.linspace(vmin, vmax, nbins+1)

        hist_channels = np.array([
            np.histogram(array[..., i], bins=nbins, range=hist_range)[0]
            for i in range(3)
        ]).T  # shape = (N_bins-1, 3)
        return hist_channels, bin_edges
    return None


def save_hist(data: np.ndarray, data_hist: np.ndarray, bins: np.ndarray,
              title: str = 'Image Histogram', informations: str = '',
              file_path: str = '', x_label: str = '', y_label: str = '') -> bool:
    """
    Create a PNG from histogram data.
    """
    # Text positionning
    mean_data = np.mean(data)
    std_data = np.std(data)
    if data.ndim == 2:
        x_text_pos = 0.30 if mean_data > bins[len(bins)//2] else 0.95
    else:
        luminance = 0.299 * data[..., 0] + 0.587 * data[..., 1] + 0.114 * data[..., 2]
        mean_lum = np.mean(luminance)
        x_text_pos = 0.30 if mean_data > mean_lum else 0.95


    # --- Création du graphique ---
    plt.figure(figsize=(10, 8), dpi=150)
    ax = plt.gca()

    # --- Tracé du ou des histogrammes ---
    if data.ndim == 2:  # image en niveaux de gris
        plt.bar(bins[:-1], data_hist, width=np.diff(bins),
                edgecolor='black', alpha=0.75, color='gray')
    elif data.ndim == 3:  # image couleur
        colors = ['red', 'green', 'blue']
        for i, c in enumerate(colors):
            plt.bar(bins[:-1], data_hist[:, i], width=np.diff(bins),
                    edgecolor='black', alpha=0.75, color=c, label=c.upper())

        # Histogramme de luminance
        luminance = 0.299 * data[..., 0] + 0.587 * data[..., 1] + 0.114 * data[..., 2]
        hist_lum, _ = np.histogram(luminance, bins=bins)
        plt.bar(bins[:-1], hist_lum, width=np.diff(bins),
                edgecolor='black', alpha=0.5, color='black', label='Luminosity')
        plt.legend()
    else:
        raise ValueError("Data dimension must be 2D (grayscale) or 3D (color).")

    # --- Informations principales ---
    text_lines = [f'Mean = {mean_data:.2f}', f'StdDev = {std_data:.2f}']

    # --- Stats par canal si image couleur ---
    if data.ndim == 3:
        for i, c in enumerate(['R', 'G', 'B']):
            text_lines.append(f'Mean {c} = {data[:,:,i].mean():.2f}')
            text_lines.append(f'StdDev {c} = {data[:,:,i].std():.2f}')

    # --- Ajout des textes sur la figure ---
    plt.text(x_text_pos, 0.95, '\n'.join(text_lines), fontsize=9,
             verticalalignment='top', horizontalalignment='right',
             transform=ax.transAxes, bbox=dict(facecolor='white', alpha=0.5))

    if informations:
        plt.text(x_text_pos, 0.25, informations, fontsize=8, verticalalignment='top',
                 horizontalalignment='right', transform=ax.transAxes,
                 bbox=dict(facecolor='white', alpha=0.5))

    # --- Titres et labels ---
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    # --- Sauvegarde ---
    if file_path:
        plt.savefig(file_path, bbox_inches='tight')
        plt.close()
        return True
    return False
