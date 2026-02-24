import sys, time
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (
    QFileDialog, QMessageBox, QPushButton, QComboBox, QRadioButton,
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QHBoxLayout, QLabel, QFormLayout, QGroupBox
)

from lensepy import translate
from lensepy.utils import *
from lensepy.widgets import *

class NucleoParamsWidget(QWidget):

    board_connected = pyqtSignal(int)

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
        layout.addStretch()
        self.setLayout(layout)

    def handle_nucleo_connected(self):
        """Action performed when the piezo button is clicked."""
        board_number = self.boards_list_box.currentIndex()
        self.board_connected.emit(board_number)

    def set_boards_list(self, board_list):
        """Set the list of the serial port connected."""
        self.boards_list = board_list
        if len(board_list) != 0:
            self.boards_list_box.addItems(self.boards_list)
            self.board_connect_button.setStyleSheet(unactived_button)
            self.board_connect_button.setEnabled(True)
        self.update()

    def set_connected(self):
        """If a board is connected, disable connexion button."""
        self.board_connect_button.setEnabled(False)
        self.board_connect_button.setStyleSheet(actived_button)
        self.board_connect_button.setText(translate('piezo_connected'))
        self.boards_list_box.setEnabled(False)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = NucleoParamsWidget()
    w.resize(400, 400)
    w.show()
    sys.exit(app.exec())

