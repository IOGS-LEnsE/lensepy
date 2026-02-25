import sys, time
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (
    QFileDialog, QMessageBox, QPushButton, QComboBox, QRadioButton,
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QHBoxLayout, QLabel, QFormLayout, QGroupBox, QProgressBar
)

from lensepy import translate
from lensepy.utils import *
from lensepy.widgets import *

class NucleoParamsWidget(QWidget):

    board_connected = pyqtSignal(int)
    acq_started = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent
        self.boards_list = None

        # Graphical objects
        layout = QVBoxLayout()

        layout.addWidget(make_hline())
        label = QLabel(translate('nucleo_params_title'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(make_hline())
        self.boards_list_box = QComboBox()
        layout.addWidget(self.boards_list_box)
        self.board_connect_button = QPushButton(translate('nucleo_connect'))
        self.board_connect_button.setStyleSheet(disabled_button)
        self.board_connect_button.setEnabled(False)
        self.board_connect_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        layout.addWidget(self.board_connect_button)
        self.board_connect_button.clicked.connect(self.handle_nucleo_connected)
        layout.addWidget(make_hline())
        self.acq_start_button = QPushButton(translate('nucleo_start_acq'))
        self.acq_start_button.setStyleSheet(disabled_button)
        self.acq_start_button.setEnabled(False)
        self.acq_start_button.setFixedHeight(BUTTON_HEIGHT)
        layout.addWidget(self.acq_start_button)
        layout.addWidget(make_hline())

        layout.addStretch()
        self.setLayout(layout)

        # Signal
        self.acq_start_button.clicked.connect(self.handle_acq_started)

    def handle_nucleo_connected(self):
        """Action performed when the piezo button is clicked."""
        board_number = self.boards_list_box.currentIndex()
        self.board_connected.emit(board_number)

    def handle_acq_started(self):
        """Action performed when the start acquisition button is clicked."""
        self.acq_started.emit()

    def set_boards_list(self, board_list):
        """Set the list of the serial port connected."""
        self.boards_list = board_list
        if len(board_list) != 0:
            self.boards_list_box.addItems(self.boards_list)
            self.board_connect_button.setStyleSheet(unactived_button)
            self.board_connect_button.setEnabled(True)
        self.update()

    def set_connected(self, version):
        """If a board is connected, disable connexion button.
        :param version:     Version of the hardware.
        """
        self.board_connect_button.setEnabled(False)
        self.board_connect_button.setStyleSheet(actived_button)
        self.board_connect_button.setText(f'{translate('nucleo_connected')} / V.{version}')
        self.boards_list_box.setEnabled(False)
        self.acq_start_button.setStyleSheet(unactived_button)
        self.acq_start_button.setEnabled(True)

    def set_acquisition(self, value = True):
        """Set acquisition mode."""
        if value:
            self.acq_start_button.setStyleSheet(actived_button)
            self.acq_start_button.setText(translate('stop_acq_button'))
        else:
            self.acq_start_button.setStyleSheet(unactived_button)
            self.acq_start_button.setText(translate('start_acq_button'))

class CoincidenceDisplayWidget(QWidget):
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
        label = QLabel(translate('coincidence_params_title'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(make_hline())

        label_abc = QLabel(translate('A_B_C_values'))
        label_abc.setStyleSheet(styleH3)
        label_abc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label_abc)
        layout.addWidget(make_hline())

        # Sliders for ABC
        abc_widget = QWidget()
        abc_layout = QHBoxLayout()
        abc_layout.addWidget(make_hline())
        self.max_value = 100
        ## A counter
        self.a_value = VerticalGauge(title='A',min_value=0, max_value=self.max_value)
            #SliderBlocVertical('A', '', 0, self.max_value, integer=True)
        abc_layout.addWidget(self.a_value)
        ## B counter
        self.b_value = SliderBlocVertical('B', '', 0, self.max_value, integer=True)
        abc_layout.addWidget(self.b_value)
        ## C counter
        self.c_value = SliderBlocVertical('C', '', 0, self.max_value, integer=True)
        abc_layout.addWidget(self.c_value)

        ## White 1
        w1_widget = QWidget()
        w1_layout = QVBoxLayout()
        w1_widget.setLayout(w1_layout)
        self.w1_color = SliderBlocVertical('W1', '', 0, 255, integer=True)
        w1_layout.addWidget(self.w1_color)
        ## White 2
        w2_widget = QWidget()
        w2_layout = QVBoxLayout()
        w2_widget.setLayout(w2_layout)
        self.w2_color = SliderBlocVertical('W2', '', 0, 255, integer=True)
        w2_layout.addWidget(self.w2_color)

        self.a_value.setEnabled(False)
        self.b_value.set_enabled(False)
        self.c_value.set_enabled(False)
        abc_layout.addWidget(make_vline())
        abc_layout.addWidget(make_vline())
        layout.addLayout(abc_layout)

        layout.addStretch()
        self.setLayout(layout)

    def set_a_b_c(self, a_cnt, b_cnt, c_cnt=0):
        """Update A B C gauges."""
        self.a_value.set_value(int(a_cnt))
        self.b_value.set_value(b_cnt)
        self.c_value.set_value(c_cnt)
        self.repaint()

    def set_max_values(self, value=100000):
        """Set maximum value of the gauges."""
        self.max_value = value


class VerticalGauge(QWidget):

    def __init__(self, parent=None, title="", min_value=0, max_value=100):
        """Create a vertical gauge.
        :param title: Title of the gauge.
        :param min_value: Minimum value of the gauge.
        :param max_value: Maximum value of the gauge.
        """
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Label au-dessus
        self.label = QLabel(title)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(styleH2)
        layout.addWidget(self.label)

        # Barre verticale
        self.progress = QProgressBar()
        self.progress.setOrientation(Qt.Orientation.Vertical)
        self.progress.setRange(min_value, max_value)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.progress.setMinimumWidth(100)

        layout.addWidget(self.progress, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Custom Style
        self.progress.setStyleSheet(progressBar)

        self.value_label = QLabel(title)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet(styleH3)
        layout.addWidget(self.value_label)

        self.setLayout(layout)

    def set_value(self, value):
        """
        Update the value of the gauge.
        :param value: value to set
        """
        self.progress.setValue(value)
        self.value_label.setText(str(value))
        self.repaint()

    def set_min_max_values(self, min_value, max_value):
        """
        Set min and max values.
        :param min_value: min value
        :param max_value: max value
        """
        self.progress.setRange(min_value, max_value)

    def set_title(self, text):
        """
        Set the title of the gauge.
        :param text: title
        """
        self.label.setText(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = VerticalGauge(title='Test', min_value=0, max_value=100)
    w.set_value(76)
    w.resize(400, 400)
    w.show()
    sys.exit(app.exec())

