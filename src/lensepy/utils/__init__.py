from .images import *

def is_float(element: any) -> bool:
    """
    Return if any object is a float number.
    :param element: Object to test.
    :return: True if the object is a float number.
    """
    # If you expect None to be passed:
    if element is None:
        return False
    try:
        float(element)
        return True
    except ValueError:
        return False

def is_integer(s: str) -> bool:
    """
    Test if string is an integer.
    :param s:   string to test.
    :return:    True if string is an integer.
    """
    try:
        # Remove spaces
        s = s.strip()
        # Try to convert s to int
        int(s)
        return True
    except ValueError:
        return False

def downsample_array(array, factor=1):
    N, M = array.shape
    N2 = (N // factor) * factor
    M2 = (M // factor) * factor
    array_crop = array[:N2, :M2]
    return array_crop.reshape(N2//factor, factor, M2//factor, factor).mean(axis=(1, 3))