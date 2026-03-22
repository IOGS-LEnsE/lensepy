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