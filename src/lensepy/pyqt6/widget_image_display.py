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
from lensepy.css import *
import cv2

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QGridLayout, QVBoxLayout,
    QLabel, QPushButton,
    QMessageBox, QScrollArea
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal

styleH2 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};font-weight: bold;"
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"
# %% Params
BUTTON_HEIGHT = 60 #px
OPTIONS_BUTTON_HEIGHT = 20 #px


class ImageDisplayWidget(QWidget):
    """WidgetImageDisplay class, children of QWidget.

    Class to display an image (array) in a widget.

    """

    window_closed = pyqtSignal(str)

    def __init__(self, zoom_params: bool = False) -> None:
        """Default constructor of the class.
        """
        super().__init__(parent=None)
        # List of the available camera
        self.main_layout = QGridLayout()
        self.image = np.zeros((10,10,3))
        self.image_disp = self.image
        self.zoom_params = zoom_params      # If true, display a menu to zoom in/out

        # Graphical objects
        self.image_area = QScrollArea()
        self.image_area.setWidgetResizable(True)
        self.image_display = QLabel('Image to display')
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_area.setWidget(self.image_display)
        self.menu_widget = ImageDisplayParams(self, title="Image Zoom")

        self.main_layout.addWidget(self.image_area, 0, 1)

        if self.zoom_params is True:
            self.main_layout.addWidget(self.menu_widget, 0, 0)
            self.main_layout.setColumnStretch(1, 9)
            self.main_layout.setColumnStretch(0, 1)
            self.update_image_params()
        self.setLayout(self.main_layout)

    def set_image_from_array(self, pixels: np.ndarray, forced: bool = True) -> None:
        """
        Display a new image from an array (Numpy)

        :param pixels: Array of pixels to display.
        :type pixels: np.ndarray

        """
        if self.zoom_params is False or forced is True:
            self.image = np.array(pixels, dtype='uint8')
            qimage = array_to_qimage(self.image)
            pmap = QPixmap(qimage)
            # pmap = QPixmap.fromImage(qimage)
            self.image_display.setPixmap(pmap.scaled(self.image_area.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                                     Qt.TransformationMode.SmoothTransformation))
            self.image_display.adjustSize()
        else:
            self.image_disp = np.array(pixels, dtype='uint8')
            qimage = array_to_qimage(self.image_disp)
            pmap = QPixmap.fromImage(qimage)
            self.image_display.setPixmap(pmap.scaled(self.image_area.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                                     Qt.TransformationMode.SmoothTransformation))
            self.image_display.adjustSize()
            self.update_image_params()

    def set_params_enabled(self, value: bool):
        """
        Set if parameters menu is displayed or not.
        """
        self.zoom_params = value
        if value is True:
            self.main_layout.addWidget(self.menu_widget, 0, 0)
            self.main_layout.setColumnStretch(1, 9)
            self.main_layout.setColumnStretch(0, 1)
            self.update_image_params()

    def update_image_params(self):
        self.menu_widget.update_properties()

    def resizeEvent(self, event):
        """Action performed when the window is resized.
        """
        if not self.image_display.pixmap().isNull():
            self.image_display.setPixmap(self.image_display.pixmap().scaled(self.image_area.size(),
                                                                            Qt.AspectRatioMode.KeepAspectRatio,
                                                                            Qt.TransformationMode.SmoothTransformation))
        super().resizeEvent(event)

    def closeEvent(self, a0):
        self.window_closed.emit('close')

    def quit_application(self) -> None:
        """
        Quit properly the PyQt6 application window.
        """
        try:
            QApplication.instance().quit()
        except Exception as e:
            print("Exception - close/quit: " + str(e) + "")


zoom_list = [25, 50, 75, 100, 125, 150, 200, 400]

def find_next_zoom(value: int, data_list: list[int]):
    '''
    Find the next integer in data_list that is greater than the given value.
    '''

    if value in data_list:
        return value

    for i, el in enumerate(data_list):
        if value < el:
            return el
        if i == len(data_list)-1:
            return data_list[len(data_list)-1]
    return value


def find_prev_zoom(value: int, data_list: list[int]):
    '''
    Find the previous integer in data_list that is lower than the given value.
    '''
    if value in data_list:
        return value

    for i, el in enumerate(data_list):
        if value < el:
            print(i)
            if i > 1 and i < len(data_list):
                return data_list[i-1]
            elif i == 0:
                return data_list[0]
            elif i == len(data_list)-1:
                return data_list[len(data_list)-1]
    return value


class ImageDisplayParams(QWidget):
    """
    Display a widget with zoom parameters
    """

    def __init__(self, parent, title='Zoom') -> None:
        """Default constructor of the class.
        """
        super().__init__(parent=None)
        self.parent = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.zoom_value = 100

        # Title
        self.label_title_params = QLabel(title)
        self.label_title_params.setStyleSheet(styleH2)
        self.label_title_params.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label_title_params)

        # Image properties
        self.label_image_height = QLabel("H = ")
        self.label_image_height.setStyleSheet(styleH3)
        self.label_image_height.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label_image_height)
        self.label_image_width = QLabel("W = ")
        self.label_image_width.setStyleSheet(styleH3)
        self.label_image_width.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label_image_width)
        self.label_zoom_value = QLabel(f"Zoom = {self.zoom_value} %")
        self.label_zoom_value.setStyleSheet(styleH3)
        self.label_zoom_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label_zoom_value)
        self.layout.addStretch()
        # Zoom button
        self.button_full_image = QPushButton('Full image')
        self.button_full_image.setStyleSheet(unactived_button)
        self.button_full_image.setFixedHeight(BUTTON_HEIGHT)
        self.layout.addWidget(self.button_full_image)
        self.button_full_image.clicked.connect(self.change_zoom)
        self.button_zoom_inc_image = QPushButton('Zoom +')
        self.button_zoom_inc_image.setStyleSheet(unactived_button)
        self.button_zoom_inc_image.setFixedHeight(BUTTON_HEIGHT)
        self.layout.addWidget(self.button_zoom_inc_image)
        self.button_zoom_inc_image.clicked.connect(self.change_zoom)
        self.button_zoom_dec_image = QPushButton('Zoom -')
        self.button_zoom_dec_image.setStyleSheet(unactived_button)
        self.button_zoom_dec_image.setFixedHeight(BUTTON_HEIGHT)
        self.layout.addWidget(self.button_zoom_dec_image)
        self.button_zoom_dec_image.clicked.connect(self.change_zoom)

        self.layout.addStretch()

    def calculate_zoom(self):
        im_height, im_width = self.parent.image.shape[0], self.parent.image.shape[1]
        wi_height, wi_width = self.parent.image_display.height(), self.parent.image_display.width()
        if im_height < wi_height and im_width < wi_width:
            self.zoom_value = 100
        else:
            if im_height > wi_height:
                ratio_h = im_height / wi_height
                self.zoom_value = round(1 / ratio_h * 100, 0)
            if im_width > wi_width:
                ratio_w = im_width / wi_width
                self.zoom_value = round(1 / ratio_w * 100, 0)
            if im_height > wi_height and im_width > wi_width:
                self.zoom_value = round(max(1 / ratio_w, 1 / ratio_h) * 100, 0)

    def change_zoom(self, event):
        im_height, im_width = self.parent.image.shape[0], self.parent.image.shape[1]
        wi_height, wi_width = self.parent.image_display.height(), self.parent.image_display.width()
        if self.sender() == self.button_full_image:
            self.calculate_zoom()
        elif self.sender() == self.button_zoom_inc_image:
            next_zoom = find_next_zoom(self.zoom_value, zoom_list)/100
            new_height = int(im_height*next_zoom)
            new_width = int(im_width*next_zoom)
            # Test if new_image > image_area size
            new_image = resize_image_ratio(self.parent.image, new_height, new_width)
            if new_image.shape[0] > wi_height or new_image.shape[1] > wi_width:
                print('Need to resize')
                pass


            self.parent.set_image_from_array(new_image, forced=False)
            print(f'Inc Zoom : {next_zoom} / {new_image.shape}')
        elif self.sender() == self.button_zoom_dec_image:
            prev_zoom = find_prev_zoom(self.zoom_value, zoom_list)/100
            #new_image = resize_image_ratio(self.parent.image, im_height*prev_zoom, im_width*prev_zoom)
            print(f'Dec Zoom : {prev_zoom}')
        self.update_properties()

    def update_properties(self):
        height, width = self.parent.image.shape[0], self.parent.image.shape[1]
        self.calculate_zoom()
        self.label_image_height.setText(f'H = {height}')
        self.label_image_width.setText(f'W = {width}')
        self.label_zoom_value.setText(f'Zoom = {self.zoom_value} %')


if __name__ == "__main__":
    import time

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
            self.setGeometry(100, 100, 800, 600)
            self.central_widget = ImageDisplayWidget(zoom_params=True)
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
    array = np.random.randint(0, 255, size=(2000, 2000), dtype=np.uint8)
    main_window.central_widget.set_image_from_array(array)
    main_window.showMaximized()

    sys.exit(app.exec())
