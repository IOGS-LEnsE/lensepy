__all__ = ["CIE1931Controller"]

from PyQt6.QtWidgets import QWidget

from lensepy.modules.cie1931.cie1931_views import CIE1931MatplotlibWidget, CoordinateTableWidget
from lensepy.appli._app.template_controller import TemplateController


class CIE1931Controller(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)

        # Graphical layout
        self.top_left = CIE1931MatplotlibWidget()
        self.bot_left = QWidget()
        self.bot_right = QWidget()
        self.top_right = CoordinateTableWidget()
        # Setup widgets

        # Signals
