__all__ = [
    "conversion",      # refers to the 'conversion.py' file
    "processing",
    "masks",
    'slice_image'
]

import numpy as np

def slice_image(image, slope : float, axis : bool = False):
    '''This global function is used in the following objects, it creates a plot from an image by slicing through it

    axis = False means the slice will be horizontal
    axis = True  means the slice will be vertical

    the sign and magnitude of the slope indicate the direction in which the slice will be taken, using this coordinate
    system:
            ^ y
            |
    --------|------> x    axis0 -> axis0 + 1
            |             axis1 -> axis1 + slope
            |
    If the slope is too big, the program will invert the axis and the slope by default and return the appropriate slice
    '''
    size = image.shape
    assert size[0] != 0 and size[1] != 0 and image is not None, "The data is not suitable : 0-dimensional array"
    if not axis:
        ax = 0
    else:
        ax = 1
    if int(size[ax] * slope) > size[not ax]:
        ax = not ax
        slope = 1/slope

    plot_x = np.linspace(0, size[ax], size[ax])
    plot_y = np.zeros(size[ax])

    for i in range(size[ax]):
        if not ax:
            plot_y[i] = image[int(slope * (i - size[ax]/2) + size[ax]/2)][i]
        else:
            plot_y[i] = image[i][int(slope * (i - size[ax]/2) + size[ax]/2)-1]

    if not ax:
        angle = np.arctan(slope) * 180/np.pi
    else:
        angle = 90 - np.arctan(slope) * 180/np.pi

    if __name__ == "__main__":
        print(f"slope = {slope}")

    return plot_x, plot_y, round(angle, 3)