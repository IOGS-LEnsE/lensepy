from PyQt6.QtCore import QSize
from PyQt6.QtGui import QBrush

from lensepy import translate
from PyQt6.QtWidgets import (
    QFileDialog, QMessageBox, QPushButton, QComboBox, QRadioButton
)
from lensepy.utils import *
from lensepy.widgets import *


class CircleWidget(QWidget):



    def __init__(self, color=QColor("red"), diameter=100):
        """Create a widget that displays a circle."""
        super().__init__()
        self.color = color
        self.diameter = diameter
        self.setMinimumSize(diameter, diameter)

    def paintEvent(self, event):
        """Draw the circle in the widget."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Color
        painter.setBrush(QBrush(self.color))
        painter.setPen(Qt.PenStyle.NoPen)
        # Process circle coordinates
        w = self.width()
        h = self.height()
        x = (w - self.diameter) / 2
        y = (h - self.diameter) / 2
        # Draw the circle
        circle_rect = QRectF(int(x), int(y), self.diameter, self.diameter)
        painter.drawEllipse(circle_rect)


class RGBLedControlWidget(QWidget):
    """
    Widget to display image opening options.
    """

    rgb_changed = pyqtSignal()
    arduino_connected = pyqtSignal(str)

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

        layout.addWidget(make_hline())

        label_rgb = QLabel(translate('R_G_B_values'))
        label_rgb.setStyleSheet(styleH3)
        label_rgb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label_rgb)

        # Sliders for RGB
        rgb_widget = QWidget()
        rgb_layout = QHBoxLayout()
        rgb_layout.addWidget(make_hline())
        ## Red
        r_widget = QWidget()
        r_layout = QVBoxLayout()
        r_widget.setLayout(r_layout)
        r_circle = CircleWidget(color=QColor(255, 0, 0), diameter=30)
        r_layout.addWidget(r_circle)
        self.r_color = SliderBlocVertical('R', '', 0, 255, integer=True)
        r_layout.addWidget(self.r_color)
        ## Green
        g_widget = QWidget()
        g_layout = QVBoxLayout()
        g_widget.setLayout(g_layout)
        g_circle = CircleWidget(color=QColor(0, 150, 0), diameter=30)
        g_layout.addWidget(g_circle)
        self.g_color = SliderBlocVertical('G', '', 0, 255, integer=True)
        g_layout.addWidget(self.g_color)
        ## Blue
        b_widget = QWidget()
        b_layout = QVBoxLayout()
        b_widget.setLayout(b_layout)
        b_circle = CircleWidget(color=QColor(0, 0, 255), diameter=30)
        b_layout.addWidget(b_circle)
        self.b_color = SliderBlocVertical('B', '', 0, 255, integer=True)
        b_layout.addWidget(self.b_color)

        ## White 1
        w1_widget = QWidget()
        w1_layout = QVBoxLayout()
        w1_widget.setLayout(w1_layout)
        w1_circle = CircleWidget(color=QColor(120, 200, 150), diameter=30)
        w1_layout.addWidget(w1_circle)
        self.w1_color = SliderBlocVertical('W1', '', 0, 255, integer=True)
        w1_layout.addWidget(self.w1_color)
        ## White 2
        w2_widget = QWidget()
        w2_layout = QVBoxLayout()
        w2_widget.setLayout(w2_layout)
        w2_circle = CircleWidget(color=QColor(120, 200, 20), diameter=30)
        w2_layout.addWidget(w2_circle)
        self.w2_color = SliderBlocVertical('W2', '', 0, 255, integer=True)
        w2_layout.addWidget(self.w2_color)

        self.r_color.set_enabled(False)
        self.g_color.set_enabled(False)
        self.b_color.set_enabled(False)
        self.w1_color.set_enabled(False)
        self.w2_color.set_enabled(False)
        rgb_layout.addWidget(r_widget)
        rgb_layout.addWidget(g_widget)
        rgb_layout.addWidget(b_widget)
        rgb_layout.addWidget(make_vline())
        rgb_layout.addWidget(w1_widget)
        rgb_layout.addWidget(w2_widget)
        layout.addLayout(rgb_layout)
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
        """Return the current RGB colors."""
        r = self.r_color.get_value()
        g = self.g_color.get_value()
        b = self.b_color.get_value()
        return (r, g, b)

    def get_w12(self):
        """Return the current W1 and W2 colors."""
        w1 = self.w1_color.get_value()
        w2 = self.w2_color.get_value()
        return (w1, w2)

    def handle_arduino_connected(self):
        self.board_connect_button.setEnabled(False)
        self.board_connect_button.setStyleSheet(disabled_button)
        self.r_color.set_enabled(True)
        self.g_color.set_enabled(True)
        self.b_color.set_enabled(True)
        self.w1_color.set_enabled(True)
        self.w2_color.set_enabled(True)
        com = self.boards_list.currentText()
        self.arduino_connected.emit(com)

