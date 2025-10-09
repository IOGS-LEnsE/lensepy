from PyQt6.QtWidgets import QWidget
import numpy as np
from lensepy.appli._app.template_controller import TemplateController
from lensepy.widgets.histogram_widget import HistogramWidget
from lensepy.pyqt6.widget_image_display import ImageDisplayWidget
from lensepy.modules.spatial_images import *


class SpatialImagesController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)
        self.top_left = ImageDisplayWithCrosshair()
        self.bot_left = HistogramWidget()
        self.bot_right = QWidget()
        self.top_right = SliceXYWidget()
        # Setup widgets
        self.bot_left.set_background('white')
        self.top_right.set_background('white')
        if self.parent.variables['bits_depth'] is not None:
            self.bot_left.set_bits_depth(int(self.parent.variables['bits_depth']))
        else:
            self.bot_left.set_bits_depth(8)
        if self.parent.variables['image'] is not None:
            self.top_left.set_image_from_array(self.parent.variables['image'])
            self.bot_left.set_image(self.parent.variables['image'])
        self.bot_left.refresh_chart()
        # Signals
        self.top_left.point_selected.connect(self.handle_xy_changed)

    def handle_xy_changed(self, x, y):
        """
        Action performed when the XY coordinates changed.
        """
        x_data = self.parent.variables['image'][int(y),:]
        xx_x = np.linspace(1, len(x_data), len(x_data))
        y_data = self.parent.variables['image'][:,int(x)]
        yy_x = np.linspace(1, len(y_data), len(y_data))
        x_slice = [xx_x, yy_x]
        y_slice = [x_data, y_data]
        self.top_right.set_data(x_slice, y_slice)
        self.top_right.refresh_chart()

    def display_image(self, image: np.ndarray):
        """
        Display the image given as a numpy array.
        :param image:   numpy array containing the data.
        :return:
        """
        self.top_left.set_image_from_array(image)


