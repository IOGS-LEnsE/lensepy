import numpy as np

def circular_mask(radius, image, inverted: bool=False, center=None):
    """
    Return an image with a circular mask.
    :param radius: Radius of the circular mask.
    :param image: Image to process.
    :param inverted: True to invert the mask.
    :return:
    """
    h, w = image.shape
    if center is None:
        center_y, center_x = h // 2, w // 2
    else:
        center_y, center_x = center
    Y, X = np.ogrid[:h, :w]
    # Distance from center to pixel
    dist_from_center = np.sqrt((X - center_x) ** 2 + (Y - center_y) ** 2)
    # Create a circular mask (1 inside the circle, 0 outside)
    if inverted:
        mask = dist_from_center > radius
    else:
        mask = dist_from_center <= radius
    return image * mask