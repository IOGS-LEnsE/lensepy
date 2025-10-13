from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QHBoxLayout, QCheckBox
from lensepy.css import *
from lensepy import translate
from lensepy.modules.basler import BaslerController, BaslerCamera
from lensepy.utils import make_hline
from lensepy.widgets import LabelWidget, SliderBloc, HistogramWidget
import numpy as np

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lensepy.modules.spatial_camera.spatial_camera_controller import SpatialCameraController


class HistoStatsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent: SpatialCameraController = parent
        self.histo_zoom = False
        self.histo = HistogramWidget()
        self.histo.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        widget_zoom = QWidget()
        layout_zoom = QHBoxLayout()
        widget_zoom.setLayout(layout_zoom)
        self.label_stats = QLabel(translate('histo_stats_title'))
        self.label_stats.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_stats.setMaximumHeight(10)
        layout = QVBoxLayout()
        layout.addWidget(self.histo, 5)
        layout.addWidget(widget_zoom, 1)
        layout_zoom.addWidget(self.label_stats)
        self.check_box = QCheckBox(translate('zoom_check_box'))
        layout_zoom.addWidget(self.check_box)
        self.check_box.checkStateChanged.connect(self.handle_zoom_changed)
        layout_zoom.addWidget(self.label_stats)
        self.setLayout(layout)

    def handle_zoom_changed(self, event):
        """

        """
        self.histo_zoom = self.check_box.isChecked()

    def set_image(self, image):
        mean_image = np.round(np.mean(image), 2)
        stdev_image = np.round(np.std(image), 2)
        str_val = f'Mean = {mean_image} / Stdev = {stdev_image}'
        self.label_stats.setText(str_val)
        self.histo.set_image(image, zoom=self.histo_zoom)

    def set_background(self, color):
        """
        Set the background color of the histogram.
        :param color: Background color.
        """
        self.histo.set_background(color)

    def set_bits_depth(self, bits_depth):
        """
        Set the bits depth of the histogram.
        :param bits_depth: Bits depth.
        """
        self.histo.set_bits_depth(bits_depth)