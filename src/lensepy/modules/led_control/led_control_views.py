from lensepy import translate
from PyQt6.QtWidgets import (
    QFileDialog, QMessageBox, QPushButton, QComboBox
)
from lensepy.utils import *
from lensepy.widgets import *


class RGBLedControlWidget(QWidget):
    """
    Widget to display image opening options.
    """

    rgb_changed = pyqtSignal()
    arduino_connected = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent    # Controller
        layout = QVBoxLayout()
        # Graphical Elements
        layout.addWidget(make_hline())

        label = QLabel(translate('led_control_dialog'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # Connection to Arduino
        layout.addWidget(make_hline())
        label_boards = QLabel(translate('led_control_boards'))
        label_boards.setStyleSheet(styleH3)
        label_boards.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label_boards)
        self.boards_list = QComboBox()
        layout.addWidget(self.boards_list)
        self.board_connect_button = QPushButton(translate('arduino_connect'))
        self.board_connect_button.setStyleSheet(unactived_button)
        self.board_connect_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        layout.addWidget(self.board_connect_button)
        self.board_connect_button.clicked.connect(self.handle_arduino_connected)

        # Sliders for RGB
        layout.addWidget(make_hline())
        label_rgb = QLabel(translate('R_G_B_values'))
        label_rgb.setStyleSheet(styleH3)
        label_rgb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label_rgb)

        self.r_color = SliderBloc('R', 'ADU', 0, 255, integer=True)
        self.g_color = SliderBloc('G', 'ADU', 0, 255, integer=True)
        self.b_color = SliderBloc('B', 'ADU', 0, 255, integer=True)
        self.r_color.set_enabled(False)
        self.g_color.set_enabled(False)
        self.b_color.set_enabled(False)
        layout.addWidget(self.r_color)
        layout.addWidget(self.g_color)
        layout.addWidget(self.b_color)
        layout.addStretch()
        self.setLayout(layout)
        # Init boards and lists
        self.boards = self.parent.wrapper.find_arduino_ports()
        if self.boards:
            self.boards_list.addItems(self.boards)
        else:
            self.board_connect_button.setEnabled(False)
            self.board_connect_button.setText(translate('no_boards'))
            self.board_connect_button.setStyleSheet(disabled_button)

        # Signals
        self.r_color.slider_changed.connect(lambda: self.rgb_changed.emit())
        self.g_color.slider_changed.connect(lambda: self.rgb_changed.emit())
        self.b_color.slider_changed.connect(lambda: self.rgb_changed.emit())

    def get_rgb(self):
        """Return the current RGB color."""
        r = self.r_color.get_value()
        g = self.g_color.get_value()
        b = self.b_color.get_value()
        return (r, g, b)

    def handle_arduino_connected(self):
        self.board_connect_button.setEnabled(False)
        self.board_connect_button.setStyleSheet(disabled_button)
        self.r_color.set_enabled(True)
        self.g_color.set_enabled(True)
        self.b_color.set_enabled(True)
        self.arduino_connected.emit()

