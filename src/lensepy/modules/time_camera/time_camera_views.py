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


class TimeOptionsWidget(QWidget):
    """
    Widget to control camera parameters and save histogram and slices.
    """

    def __init__(self):
        super().__init__()
        # Attributes
        self.image_dir = None
        # Layout
        self.layout = QVBoxLayout()
        # Graphical objects
        self.camera_params = CameraParamsDisplayWidget()
        self.layout.addWidget(self.camera_params)

        self.save_histo_button = QPushButton(translate('save_time_histo_button'))
        self.save_histo_button.setStyleSheet(unactived_button)
        self.save_histo_button.setFixedHeight(BUTTON_HEIGHT)
        self.save_histo_button.clicked.connect(self.handle_save_histogram)
        self.layout.addWidget(self.save_histo_button)
        self.save_time_chart_button = QPushButton(translate('save_time_chart_button'))
        self.save_time_chart_button.setStyleSheet(unactived_button)
        self.save_time_chart_button.setFixedHeight(BUTTON_HEIGHT)
        self.save_time_chart_button.clicked.connect(self.handle_save_time_chart)
        self.layout.addWidget(self.save_histo_button)
        self.layout.addStretch()

        self.setLayout(self.layout)

    def set_img_dir(self, filepath):
        """Set the image directory, to save histograms and time charts."""
        self.image_dir = filepath

    def handle_save_time_chart(self, event):
        self.save_time_chart_button.setStyleSheet(actived_button)
        pass

    def handle_save_histogram(self, event):
        sender = self.sender()
        self.save_histo_button.setStyleSheet(actived_button)

        self.parent.stop_live()
        image = self.parent.parent.variables['image']
        bits_depth = self.parent.parent.variables['bits_depth']
        bins = np.linspace(0, 2 ** bits_depth, 2 ** bits_depth + 1)
        plot_hist, plot_bins_data = process_hist_from_array(image, bins, bits_depth=bits_depth, zoom=True)
        save_dir = self._get_file_path(self.image_dir)
        if save_dir != '':
            save_hist(image, plot_hist, plot_bins_data, file_path=save_dir)
        self.parent.start_live()
        self.save_histo_button.setStyleSheet(unactived_button)

    def set_exposure_time(self, exposure):
        """
        Set the exposure time in microseconds.
        :param exposure: exposure time in microseconds.
        """
        self.camera_params.exposure_time.set_value(f'{exposure}')

    def set_black_level(self, black_level):
        """
        Set the black level.
        :param black_level: black level.
        """
        self.camera_params.black_level.set_value(f'{black_level}')

    def set_frame_rate(self, frame_rate):
        """
        Set the frame rate.
        :param frame_rate: frame rate.
        """
        self.camera_params.frame_rate.set_value(f'{frame_rate}')

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


class CameraParamsDisplayWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        # Graphical objects
        self.exposure_time = LabelWidget(translate('exposure_time'), '0', units='us')
        self.black_level = LabelWidget(translate('black_level'), '0', units='ADU')
        self.frame_rate = LabelWidget(translate('frame_rate'), '0', units='Hz')
        self.layout.addWidget(self.exposure_time)
        self.layout.addWidget(self.black_level)
        self.layout.addWidget(self.frame_rate)
        self.setLayout(self.layout)
