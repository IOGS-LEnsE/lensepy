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

        self.points_list = {}

        # Graphical layout
        self.top_left = CIE1931MatplotlibWidget()
        self.bot_left = QWidget()
        self.bot_right = QWidget()
        self.top_right = CoordinateTableWidget()
        # Setup widgets

        # Signals
        self.top_right.point_added.connect(self.handle_point_added)
        self.top_right.point_deleted.connect(self.handle_point_deleted)

    def handle_point_added(self, data):
        """Action performed when a new point is added."""
        self.points_list[data['name']] = data
        # Update graph ?
        self.top_left.update_list(data)
        print(self.points_list)

    def handle_point_deleted(self, data):
        """Action performed when a point is deleted."""
        self.points_list.pop(data['name'])
        # Update graph ?
        self.top_left.update_list(data)
        print(self.points_list)