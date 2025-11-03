__all__ = ["LedControlController"]

from PyQt6.QtWidgets import QWidget

from lensepy.modules.led_control.led_control_views import RGBLedControlWidget
from lensepy.modules.led_control.led_control_model import *
from lensepy.appli._app.template_controller import TemplateController


class LedControlController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)
        # LED wrapper
        self.wrapper = RGBLedWrapper()
        # Graphical layout
        self.top_left = RGBLedControlWidget(self)
        self.bot_left = QWidget()
        self.bot_right = QWidget()
        self.top_right = QWidget()
        # Setup widgets

        # Signals
        self.top_left.rgb_changed.connect(self.handle_rgb_changed)


    def handle_rgb_changed(self):
        """Action performed when RGB sliders changed."""
        r, g, b = self.top_left.get_rgb()
        print(r, g, b)




