# -*- coding: utf-8 -*-
"""*widget_image_display.py* file.

*widget_image_display* file that contains :class::WidgetImageDisplay
to display an image in a widget

.. note:: LEnsE - Institut d'Optique - version 0.1

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>
"""
import sys
import numpy as np

from lensepy.images.conversion import *

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QGridLayout,
    QLabel,
    QMessageBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class WidgetImageDisplay(QWidget):
    """WidgetImageDisplay class, children of QWidget.

    Class to display an image (array) in a widget.

    """

    def __init__(self) -> None:
        """Default constructor of the class.
        """
        super().__init__(parent=None)
        # List of the available camera
        self.main_layout = QGridLayout()
        self.image = np.zeros((10,10,3))

        # Graphical objects
        self.image_display = QLabel('Image to display')
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.image_display)

        self.setLayout(self.main_layout)

    def set_image_from_array(self, pixels: np.ndarray) -> None:
        """
        Display a new image from an array (Numpy)

        :param pixels: Array of pixels to display.
        :type pixels: np.ndarray

        """
        try:
            self.image = pixels
            self.resizeEvent(None)
        except Exception as e:
            print("Exception - refresh: " + str(e) + "")

    def resizeEvent(self, event):
        """Action performed when the window is resized.
        """
        try:
            # Get widget size
            frame_width = self.width() - 30
            frame_height = self.height() - 30

            height, width = self.image.shape[:2]
            if frame_height < height and frame_width < width:
                # Resize to the display size
                image_array_disp2 = resize_image_ratio(
                    self.image,
                    frame_height,
                    frame_width)
                # Convert the frame into an image
                image = array_to_qimage(image_array_disp2)
            else:
                image = array_to_qimage(self.image)
            pmap = QPixmap(image)
            # display it in the cameraDisplay
            self.image_display.setPixmap(pmap)
        except Exception as e:
            print("Exception - resize_event: " + str(e) + "")

    def quit_application(self) -> None:
        """
        Quit properly the PyQt6 application window.
        """
        try:
            QApplication.instance().quit()
        except Exception as e:
            print("Exception - close/quit: " + str(e) + "")


if __name__ == "__main__":

    class MyMainWindow(QMainWindow):
        """MyMainWindow class, children of QMainWindow.

        Class to test the previous widget.

        """

        def __init__(self) -> None:
            """
            Default constructor of the class.
            """
            super().__init__()
            self.setWindowTitle("WidgetImageDisplay Test Window")
            self.setGeometry(100, 100, 100, 100)
            self.central_widget = WidgetImageDisplay()
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
                self.central_widget.quit_application()
                event.accept()
            else:
                event.ignore()


    app = QApplication(sys.argv)
    main_window = MyMainWindow()
    main_window.show()

    array = 52*np.ones((300, 400, 3), dtype=np.uint8)

    main_window.central_widget.set_image_from_array(array)

    sys.exit(app.exec())
