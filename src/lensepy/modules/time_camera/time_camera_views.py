import cv2
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QHBoxLayout, QCheckBox, QPushButton, QFileDialog, \
    QMessageBox
from lensepy.css import *
from lensepy import translate
from lensepy.modules.basler import BaslerController, BaslerCamera
from lensepy.utils import make_hline, process_hist_from_array, save_hist
from lensepy.widgets import LabelWidget, SliderBloc, HistogramWidget, CameraParamsWidget
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
        self.check_box.stateChanged.connect(self.handle_zoom_changed)
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


class HistoSaveWidget(CameraParamsWidget):
    """
    Widget to control camera parameters and save histogram and slices.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Attributes
        self.image_dir = self.parent.img_dir
        # Graphical objects
        self.save_histo_button = QPushButton(translate('save_histo_button'))
        self.save_histo_button.setStyleSheet(unactived_button)
        self.save_histo_button.setFixedHeight(BUTTON_HEIGHT)
        self.save_histo_button.clicked.connect(self.handle_save_histogram)
        self.layout().addWidget(self.save_histo_button)
        self.save_histo_zoom_button = QPushButton(translate('save_histo_zoom_button'))
        self.save_histo_zoom_button.setStyleSheet(unactived_button)
        self.save_histo_zoom_button.setFixedHeight(BUTTON_HEIGHT)
        self.save_histo_zoom_button.clicked.connect(self.handle_save_histogram)
        self.layout().addWidget(self.save_histo_zoom_button)
        self.save_slice_button = QPushButton(translate('save_slice_button'))
        self.save_slice_button.setStyleSheet(unactived_button)
        self.save_slice_button.setFixedHeight(BUTTON_HEIGHT)
        self.save_slice_button.clicked.connect(self.handle_save_slice)
        self.layout().addWidget(self.save_slice_button)
        self.layout().addStretch()

    def handle_save_slice(self, event):
        self.save_slice_button.setStyleSheet(actived_button)
        pass

    def handle_save_histogram(self, event):
        sender = self.sender()
        if sender == self.save_histo_button:
            self.save_histo_button.setStyleSheet(actived_button)
        elif sender == self.save_histo_zoom_button:
            self.save_histo_zoom_button.setStyleSheet(actived_button)

        self.parent.stop_live()
        image = self.parent.parent.variables['image']
        bits_depth = self.parent.parent.variables['bits_depth']
        bins = np.linspace(0, 2 ** bits_depth, 2 ** bits_depth + 1)
        if sender == self.save_histo_button:
            plot_hist, plot_bins_data = process_hist_from_array(image, bins, bits_depth=bits_depth)
        elif sender == self.save_histo_zoom_button:
            plot_hist, plot_bins_data = process_hist_from_array(image, bins, bits_depth=bits_depth, zoom=True)
        save_dir = self._get_file_path(self.image_dir)
        if save_dir != '':
            save_hist(image, plot_hist, plot_bins_data, file_path=save_dir)
        self.parent.start_live()
        self.save_histo_button.setStyleSheet(unactived_button)
        self.save_histo_zoom_button.setStyleSheet(unactived_button)

    def _get_file_path(self, default_dir: str = '') -> bool:
        """
        Open an image from a file.
        """
        file_dialog = QFileDialog()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            translate('dialog_save_histoe'),
            default_dir,
            "Images (*.png)"
        )

        if file_path != '':
            print(f'Saving path {file_path}')
            return file_path
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning - No File Loaded")
            dlg.setText("No Image File was loaded...")
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Ok
            )
            dlg.setIcon(QMessageBox.Icon.Warning)
            button = dlg.exec()
            return ''