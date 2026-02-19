__all__ = ["PiezoDMDController"]

import time
from PyQt6.QtWidgets import QWidget
from lensepy.widgets import ImageDisplayWidget

from lensepy.modules.drivers.piezo_dmd.piezo_dmd_views import *
from lensepy.appli._app.template_controller import TemplateController


class PiezoDMDController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)
        # DMD wrapper
        #self.DMD_wrapper = RGBLedWrapper()
        # Piezo-Nucleo wrapper
        #self.piezo_wrapper = RGBLedWrapper()
        # Graphical layout
        self.top_left = ImageDisplayWidget()
        self.bot_left = QWidget()
        self.top_right = DMDParamsView()
        self.bot_right = QWidget()
        # Setup widgets

        # Signals
        #self.top_left.arduino_connected.connect(self.handle_arduino_connected)

    def handle_arduino_connected(self, com):
        """Action performed when arduino is connected."""
        self.wrapper.connect_arduino(com)



