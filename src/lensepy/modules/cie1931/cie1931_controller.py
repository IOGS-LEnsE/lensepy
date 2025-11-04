__all__ = ["LedControlController"]

from PyQt6.QtWidgets import QWidget

from lensepy.modules.led_control.led_control_views import RGBLedControlWidget
from lensepy.modules.led_control.led_control_model import *
from lensepy.appli._app.template_controller import TemplateController


class CIE1931Controller(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)

        # Graphical layout
        self.top_left = QWidget()
        self.bot_left = QWidget()
        self.bot_right = QWidget()
        self.top_right = QWidget()
        # Setup widgets

        # Signals
