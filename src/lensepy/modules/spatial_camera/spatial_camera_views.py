from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from lensepy.css import *
from lensepy import translate
from lensepy.modules.basler import BaslerController, BaslerCamera
from lensepy.utils import make_hline
from lensepy.widgets import LabelWidget, SliderBloc


class CameraParamsWidget(QWidget):
    """
    Widget to display image infos.
    """
    exposure_time_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent: BaslerController = parent
        layout = QVBoxLayout()

        self.camera = self.parent.get_variables()['camera']

        label = QLabel(translate('basler_params_title'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(make_hline())

        self.label_fps = LabelWidget(translate('basler_params_fps'), '')
        layout.addWidget(self.label_fps)
        self.slider_expo = SliderBloc(translate('basler_params_slider_expo'), unit='us',
                                      min_value=20, max_value=100000, integer=True)
        self.slider_expo.slider.setEnabled(False)
        layout.addWidget(self.slider_expo)
        layout.addWidget(make_hline())

        self.slider_expo.slider_changed.connect(self.handle_exposure_time_changed)

        layout.addStretch()
        self.setLayout(layout)

    def handle_exposure_time_changed(self, value):
        """
        Action performed when color mode is changed.
        """
        self.exposure_time_changed.emit(int(value))

    def update_infos(self):
        """
        Update information from camera.
        """
        self.camera: BaslerCamera = self.parent.get_variables()['camera']
        if self.parent.camera_connected:
            self.camera.open()
            self.label_name.set_value(self.camera.get_parameter('DeviceModelName'))
            self.label_serial.set_value(self.camera.get_parameter('DeviceSerialNumber'))
            w = str(self.camera.get_parameter('SensorWidth'))
            h = str(self.camera.get_parameter('SensorHeight'))
            self.label_size.set_value(f'WxH = {w} x {h}')
            self.camera.close()
        else:
            self.label_name.set_value(translate('no_camera'))
            self.label_serial.set_value(translate('no_camera'))
            self.label_size.set_value('')
