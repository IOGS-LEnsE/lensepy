# -*- coding: utf-8 -*-
"""*widget_combobox* file.

*widget_combobox* file that contains :class::ComboBoxBloc

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>

"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QCheckBox, QSlider, QLineEdit,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QTimer, Qt
import numpy as np
from lensepy import load_dictionary, translate
from lensepy.css import *

# %% Widget
class ComboBoxBloc(QWidget):
    selection_changed = pyqtSignal(str)

    def __init__(self, title: str, list_options: list, default: bool = True) -> None:
        super().__init__(parent=None)

        self.layout = QHBoxLayout()

        self.label = QLabel(translate(title))
        self.label.setStyleSheet(styleH2)

        self.combobox = QComboBox()
        if default:
            self.combobox.addItem(translate('select_option_default'))
        self.combobox.setCurrentIndex(0)
        self.combobox.addItems(list_options)
        self.combobox.setStyleSheet(styleH3)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.combobox)

        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.combobox.currentTextChanged.connect(self.emit_selection_changed)

    def emit_selection_changed(self, text):
        self.selection_changed.emit(text)

    def update_options(self, list_options):
        self.combobox.clear()
        self.combobox.addItem(translate('select_option_default'))
        self.combobox.setCurrentIndex(0)
        self.combobox.addItems(list_options)

    def get_text(self):
        return self.combobox.currentText()

    def get_index(self):
        return self.combobox.currentIndex()

# %% Example
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication


    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            # Translation
            dictionary = {}
            # Load French dictionary
            # dictionary = load_dictionary('../lang/dict_FR.txt')
            # Load English dictionary
            dictionary = load_dictionary('../lang/dict_EN.txt')

            self.setWindowTitle(translate("window_title_combo_box_block"))
            self.setGeometry(300, 300, 600, 600)

            self.central_widget = ComboBoxBloc(title='Title', list_options=['opt1', 'opt2'])
            self.setCentralWidget(self.central_widget)

        def closeEvent(self, event):
            """
            closeEvent redefinition. Use when the user clicks
            on the red cross to close the window
            """
            reply = QMessageBox.question(self, 'Quit', 'Do you really want to close ?',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()


    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
