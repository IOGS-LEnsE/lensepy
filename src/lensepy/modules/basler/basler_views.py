from PyQt6.QtWidgets import QLineEdit, QSlider, QGridLayout, QPushButton

from lensepy import translate
from lensepy.utils import is_integer
from lensepy.utils.pyqt6 import make_hline
from lensepy.widgets import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lensepy.modules.basler.basler_controller import BaslerController

class CameraInfosWidget(QWidget):
    """
    Widget to display image infos.
    """
    color_mode_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent: BaslerController = parent  # BaslerController or any CameraController
        layout = QVBoxLayout()

        self.camera = self.parent.get_variables()['camera']

        label = QLabel(translate('basler_infos_title'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(make_hline())

        self.label_name = LabelWidget(translate('basler_infos_name'), '')
        layout.addWidget(self.label_name)
        self.label_serial = LabelWidget(translate('basler_infos_serial'), '')
        layout.addWidget(self.label_serial)
        layout.addWidget(make_hline())

        self.label_size = LabelWidget(translate('basler_infos_size'), '', 'pixels')
        layout.addWidget(self.label_size)
        self.color_choice = self.parent.colormode
        self.label_color_mode = SelectWidget(translate('basler_infos_color_mode'), self.color_choice)
        self.label_color_mode.choice_selected.connect(self.handle_color_mode_changed)
        layout.addWidget(self.label_color_mode)
        layout.addWidget(make_hline())

        self.roi_widget = CameraROIWidget(self.parent)
        layout.addWidget(self.roi_widget)

        layout.addStretch()
        self.setLayout(layout)
        #self.update_infos()

    def set_initial_roi(self, x0: int, y0: int, x1: int, y1: int):
        """
        Set initial values for ROI.
        :param x0: X coordinate of the top-left corner of the ROI.
        :param y0: Y coordinate of the top-left corner of the ROI.
        :param x1: X coordinate of the bottom-right corner of the ROI.
        :param y1: Y coordinate of the bottom-right corner of the ROI.
        """
        self.roi_widget.init_range()    # Camera is initialized - Get range
        self.roi_widget.set_initial_roi(x0, y0, x1, y1)

    def handle_color_mode_changed(self, event):
        """
        Action performed when color mode is changed.
        """
        self.color_mode_changed.emit(event)

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


class CameraROIWidget(QWidget):
    """
    Widget to select ROI of an image.
    """
    roi_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent: BaslerController = parent
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.coords = [0, 0, 0, 0]   # x0, y0, x1, y1
        self.camera_range = [0, 0, 0, 0]    # x0max, y0max, x1max, y1max
        # ROI Checkbox
        self.roi_widget = ROIChecker()
        self.roi_widget.roi_checked.connect(self.handle_roi_checked)
        layout.addWidget(self.roi_widget)
        layout.addWidget(make_hline())
        # X0, Y0, X1, Y1, W, H widget
        self.roi_select = ROISelectWidget()
        self.roi_select.roi_changed.connect(self.handle_roi_selected)
        layout.addWidget(self.roi_select)
        self.center_roi_button = QPushButton(translate('roi_center_button'))
        self.center_roi_button.setStyleSheet(disabled_button)
        self.center_roi_button.setFixedHeight(BUTTON_HEIGHT)
        self.center_roi_button.setEnabled(False)
        self.center_roi_button.clicked.connect(self.handle_roi_centered)
        layout.addWidget(self.center_roi_button)
        self.reset_roi_button = QPushButton(translate('roi_reset_button'))
        self.reset_roi_button.setStyleSheet(disabled_button)
        self.reset_roi_button.setFixedHeight(BUTTON_HEIGHT)
        self.reset_roi_button.setEnabled(False)
        self.reset_roi_button.clicked.connect(self.handle_roi_reset)
        layout.addWidget(self.reset_roi_button)

    def init_range(self):
        camera = self.parent.parent.variables['camera']
        if camera is not None:
            self.camera_range = [0, 0, camera.get_parameter('WidthMax'), camera.get_parameter('HeightMax')]

    def handle_roi_checked(self, value: bool):
        """
        Action performed when ROI is checked.
        :param value: ROI checked value.
        """
        self.roi_select.set_enabled(value)
        self.center_roi_button.setEnabled(value)
        self.reset_roi_button.setEnabled(value)
        # Change button display
        button_mode = disabled_button if not value else unactived_button
        self.center_roi_button.setStyleSheet(button_mode)
        self.reset_roi_button.setStyleSheet(button_mode)

    def handle_roi_centered(self):
        """Recalculate ROI position to centering it."""
        new_w = self.coords[2] - self.coords[0]
        new_x0 = (self.camera_range[2] - self.camera_range[0]) // 2 - new_w // 2
        new_x1 = (self.camera_range[2] - self.camera_range[0]) // 2 + new_w // 2
        new_h = self.coords[3] - self.coords[1]
        new_y0 = (self.camera_range[3] - self.camera_range[1]) // 2 - new_h // 2
        new_y1 = (self.camera_range[3] - self.camera_range[1]) // 2 + new_h // 2
        self.coords = [new_x0, new_y0, new_x1, new_y1]
        self.set_initial_roi(self.coords[0], self.coords[1], self.coords[2], self.coords[3])

    def handle_roi_reset(self):
        """Reset ROI to the maximum range of the camera."""
        self.coords = self.camera_range
        self.set_initial_roi(self.coords[0], self.coords[1], self.coords[2], self.coords[3])

    def handle_roi_selected(self, x0:int, y0:int, x1:int, y1:int):
        """
        Action performed when ROI is selected.
        :param x0: X coordinate of the top-left corner of the ROI.
        :param y0: Y coordinate of the top-left corner of the ROI.
        :param x1: X coordinate of the bottom-right corner of the ROI.
        :param y1: Y coordinate of the bottom-right corner of the ROI.
        """
        coords = [x0, y0, x1, y1]
        # Test if x0, y0, x1 and y1 are in the good range (defined by camera)
        check_range = self.check_roi_range(coords)
        if check_range:
            self.coords = coords
        else:
            if x0 < self.camera_range[0]:
                x0 = self.coords[0]
            elif y0 < self.camera_range[1]:
                y0 = self.coords[1]
            elif x1 > self.camera_range[2]:
                x1 = self.coords[2]
            elif y1 > self.camera_range[3]:
                y1 = self.coords[3]
            self.roi_select.set_initial_values(x0, y0, x1, y1)

    def set_initial_roi(self, x0: int, y0: int, x1: int, y1: int):
        """
        Set initial values for ROI.
        :param x0: X coordinate of the top-left corner of the ROI.
        :param y0: Y coordinate of the top-left corner of the ROI.
        :param x1: X coordinate of the bottom-right corner of the ROI.
        :param y1: Y coordinate of the bottom-right corner of the ROI.
        """
        self.coords = [x0, y0, x1, y1]
        self.roi_select.set_initial_values(x0=x0, y0=y0, x1=x1, y1=y1)

    def check_roi_range(self, coords: list):
        """
        Check ROI range, if in the camera range.
        :param coords: ROI coordinates.
        """
        if (coords[0] < self.camera_range[0] or coords[2] > self.camera_range[2]
                or coords[1] < self.camera_range[1] or coords[3] > self.camera_range[3]):
            return False
        else:
            return True


class ROIChecker(QWidget):
    roi_checked = pyqtSignal(bool)
    def __init__(self, parent=None):
        super().__init__(None)
        roi_layout = QHBoxLayout()
        self.setLayout(roi_layout)
        self.check_roi = QCheckBox()
        self.check_roi.stateChanged.connect(self.handle_roi_checked)
        roi_layout.addWidget(self.check_roi, 1)
        label = QLabel(translate('camera_roi_title'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        roi_layout.addWidget(label, 4)

    def handle_roi_checked(self):
        self.roi_checked.emit(self.check_roi.isChecked())


class ROISelectWidget(QWidget):
    roi_changed = pyqtSignal(int, int, int, int)
    def __init__(self, parent=None):
        super().__init__(None)
        layout = QGridLayout()
        self.setLayout(layout)
        self.x0_label = LineEditWidget(translate('roi_x0'), value='')
        self.x0_label.setStyleSheet(styleH2)
        self.y0_label = LineEditWidget(translate('roi_y0'), value='')
        self.y0_label.setStyleSheet(styleH2)
        self.x1_label = LineEditWidget(translate('roi_x1'), value='')
        self.x1_label.setStyleSheet(styleH2)
        self.y1_label = LineEditWidget(translate('roi_y1'), value='')
        self.y1_label.setStyleSheet(styleH2)
        # Width and Height
        self.w_label = LineEditWidget(translate('roi_w'), value='')
        self.w_label.setStyleSheet(styleH2)
        self.h_label = LineEditWidget(translate('roi_h'), value='')
        self.h_label.setStyleSheet(styleH2)
        # All disabled
        self.set_enabled(False)
        self.x0_old = 0
        self.y0_old = 0
        self.x1_old = 0
        self.y1_old = 0
        self.width_old = 0
        self.height_old = 0

        layout.addWidget(self.x0_label, 0, 0)
        layout.addWidget(self.y0_label, 0, 1)
        layout.addWidget(self.x1_label, 1, 0)
        layout.addWidget(self.y1_label, 1, 1)
        layout.addWidget(self.w_label, 2, 0)
        layout.addWidget(self.h_label, 2, 1)

        # Signals
        self.x0_label.edit_changed.connect(self.handle_edit_changed)
        self.y0_label.edit_changed.connect(self.handle_edit_changed)
        self.x1_label.edit_changed.connect(self.handle_edit_changed)
        self.y1_label.edit_changed.connect(self.handle_edit_changed)
        self.w_label.edit_changed.connect(self.handle_edit_changed)
        self.h_label.edit_changed.connect(self.handle_edit_changed)

    def set_initial_values(self, x0:int, y0:int, x1:int, y1:int):
        """
        Set initial values for ROI.
        :param x0: X coordinate of the top-left corner of the ROI.
        :param y0: Y coordinate of the top-left corner of the ROI.
        :param x1: X coordinate of the bottom-right corner of the ROI.
        :param y1: Y coordinate of the bottom-right corner of the ROI.
        """
        self.x0_old = x0
        self.y0_old = y0
        self.x1_old = x1
        self.y1_old = y1
        self.width_old = x1-x0
        self.height_old = y1-y0
        self.update_values()

    def update_values(self):
        self.x0_label.set_value(str(self.x0_old))
        self.y0_label.set_value(str(self.y0_old))
        self.x1_label.set_value(str(self.x1_old))
        self.y1_label.set_value(str(self.y1_old))
        self.h_label.set_value(str(self.height_old))
        self.w_label.set_value(str(self.width_old))

    def handle_edit_changed(self, value):
        """
        Action performed when ROI is edited.
        This function checks whether the value is an integer before storing it.
        :param value:   New ROI value.
        """
        sender = self.sender()
        if is_integer(value):
            if sender == self.x0_label:
                self.x0_old = int(value)
            elif sender == self.y0_label:
                self.y0_old = int(value)
            elif sender == self.x1_label:
                self.x1_old = int(value)
            elif sender == self.y1_label:
                self.y1_old = int(value)
            elif sender == self.w_label:
                # Width changed
                self.width_old = int(value)
                self.x1_old = self.x0_old + self.width_old
            elif sender == self.h_label:
                self.height_old = int(value)
                self.y1_old = self.y0_old + self.height_old

            if self.x0_old > self.x1_old:
                self.x0_old, self.x1_old = self.x1_old, self.x0_old
            if self.y0_old > self.y1_old:
                self.y0_old, self.y1_old = self.y1_old, self.y0_old
            self.roi_changed.emit(self.x0_old, self.y0_old, self.x1_old, self.y1_old)
            self.width_old = self.x1_old - self.x0_old
            self.height_old = self.y1_old - self.y0_old
            self.update_values()
        else:
            if sender == self.x0_label:
                self.x0_label.line_edit.setText(str(self.x0_old))
            elif sender == self.y0_label:
                self.y0_label.line_edit.setText(str(self.y0_old))
            elif sender == self.x1_label:
                self.x1_label.line_edit.setText(str(self.x1_old))
            elif sender == self.y1_label:
                self.y1_label.line_edit.setText(str(self.y1_old))

    def set_enabled(self, value: bool=True):
        """
        Set the widget enabled.
        :param value:   True or False.
        """
        self.x0_label.set_enabled(value)
        self.y0_label.set_enabled(value)
        self.x1_label.set_enabled(value)
        self.y1_label.set_enabled(value)
        self.w_label.set_enabled(value)
        self.h_label.set_enabled(value)


class LineEditWidget(QWidget):
    """
    Widget for line edit, including a title.
    """
    edit_changed = pyqtSignal(str)
    def __init__(self, title:str='', value='', parent=None):
        super().__init__(None)
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.value = value

        # Label
        self.label = QLabel(title)
        layout.addWidget(self.label, 1)
        # Line Edit
        self.line_edit = QLineEdit()
        self.line_edit.setText(value)
        self.line_edit.editingFinished.connect(lambda: self.edit_changed.emit(self.line_edit.text()))
        layout.addWidget(self.line_edit, 2)

    def set_value(self, value):
        """
        Set the widget value in the line edit object.
        :param value:   Value to set.
        """
        self.line_edit.setText(value)

    def set_enabled(self, value: bool=True):
        """
        Set the widget enabled.
        :param value:   True or False.
        """
        self.line_edit.setEnabled(value)

