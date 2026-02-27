from .images import *

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