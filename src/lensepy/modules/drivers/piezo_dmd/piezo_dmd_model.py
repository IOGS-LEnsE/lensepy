import serial
from serial.tools import list_ports



class DMDWrapper:
    """
    Wrapper class for a DMD xxx.
    """

    def __init__(self, parent=None):
        self.image = [None]*3


    def set_image(self, image, number=1):
        """
        Set image to send to the DMD.
        :param image:   2D array containing the image to send to the DMD.
        :param number:   Number of the image to set.
        """
        self.image[number-1] = image

    def get_image(self, number):
        """Get an image with its number."""
        return self.image[number-1]
