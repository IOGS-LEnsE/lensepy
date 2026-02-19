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


class DMDParamsView(QWidget):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super(DMDParamsView, self).__init__(parent)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = DMDParamsView()
    w.resize(400, 400)
    w.show()
    sys.exit(app.exec())

