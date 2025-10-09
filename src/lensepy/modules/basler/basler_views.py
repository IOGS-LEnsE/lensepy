import sys

import cv2
import numpy as np
from PyQt6.QtGui import QImage, QPixmap, QFont, QColor
from lensepy import translate
from lensepy.css import *
from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout,
    QWidget, QLabel, QFrame, QCheckBox, QComboBox, QApplication, QGraphicsView,
    QGraphicsScene, QGraphicsPixmapItem, QGraphicsTextItem
)
from lensepy.images.conversion import resize_image_ratio
import pyqtgraph as pg

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lensepy.modules.basler.basler_controller import BaslerController, BaslerCamera

class CameraInfosWidget(QWidget):
    """
    Widget to display image infos.
    """
    color_mode_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent: BaslerController = parent
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

        layout.addStretch()
        self.setLayout(layout)
        #self.update_infos()

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
            print(f'Basler - NO CAMERA')
            self.label_name.set_value(translate('no_camera'))
            self.label_serial.set_value(translate('no_camera'))
            self.label_size.set_value('')



# TO MOVE TO LENSEPY  --> version 2

def make_hline():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFrameShadow(QFrame.Shadow.Sunken)
    return line

def imread_rgb(path):
    """
    Open an image from a file, after RGB conversion.
    :param path:    Path to image.
    :return:        np.ndarray RGB image.
    """
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    bits_depth = img.dtype.itemsize * 8
    if img is None:
        raise ValueError(f"Invalid path : {path}")
    if img.ndim == 2:
        # Déjà en gris → on garde tel quel
        return img, bits_depth
    if img.ndim == 3:
        if img.shape[2] == 3:
            # Conversion BGR → RGB
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB), 8
        elif img.shape[2] == 4:
            # Conversion BGRA → RGBA
            return cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA), 8
    return img, bits_depth

class HistogramWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.image = None
        self.bits_depth = 8

        # Layout principal
        layout = QVBoxLayout(self)

        # Zone graphique
        self.plot = pg.PlotWidget()
        self.plot.setLabel('bottom', 'Intensity')
        self.plot.setLabel('left', 'Frequency')
        layout.addWidget(self.plot)

        # BarGraphItems for each channel
        self.bar_r = pg.BarGraphItem(x=[0], height=[0], width=1, brush=pg.mkBrush(255, 0, 0, 150))
        self.bar_g = pg.BarGraphItem(x=[0], height=[0], width=1, brush=pg.mkBrush(0, 255, 0, 150))
        self.bar_b = pg.BarGraphItem(x=[0], height=[0], width=1, brush=pg.mkBrush(0, 0, 255, 150))
        self.bar_l = pg.BarGraphItem(x=[0], height=[0], width=1, brush=pg.mkBrush(200, 200, 200, 150))

        self.plot.addItem(self.bar_r)
        self.plot.addItem(self.bar_g)
        self.plot.addItem(self.bar_b)
        self.plot.addItem(self.bar_l)

        # Checkboxes
        box_layout = QHBoxLayout()
        self.chk_r = QCheckBox("R")
        self.chk_g = QCheckBox("G")
        self.chk_b = QCheckBox("B")
        self.chk_l = QCheckBox("Lum.")
        for chk in [self.chk_r, self.chk_g, self.chk_b, self.chk_l]:
            chk.setChecked(True)
            chk.stateChanged.connect(self.refresh_chart)
            box_layout.addWidget(chk)
        layout.addLayout(box_layout)

    def reinit_checkbox(self, mode: str):
        """
        Update checkbox visibility.
        :param mode:    'RGB' or 'Gray'
        """
        # Detect if RGB or Grayscale
        if mode == 'Gray':
            for chk in [self.chk_r, self.chk_g, self.chk_b]:
                chk.setEnabled(False)
                chk.setChecked(False)
            self.chk_l.setEnabled(False)
            self.chk_l.setChecked(True)
        elif mode == 'RGB':
            for chk in [self.chk_r, self.chk_g, self.chk_b, self.chk_l]:
                chk.setChecked(True)
                chk.setEnabled(True)


    def set_image(self, img: np.ndarray, checked: bool = True):
        """Définit l'image (numpy array, 2D pour gris ou 3D pour RGB)."""
        self.image = img.copy()
        # Detect if RGB or Grayscale
        if img.ndim == 2:
            # Grayscale image
            # Update checkboxes
            if checked:
                for chk in [self.chk_r, self.chk_g, self.chk_b]:
                    chk.setEnabled(False)
                    chk.setChecked(False)
                self.chk_l.setEnabled(False)
                self.chk_l.setChecked(True)
        else:
            # RGB image
            if checked:
                for chk in [self.chk_r, self.chk_g, self.chk_b, self.chk_l]:
                    chk.setChecked(True)
                    chk.setEnabled(True)
        self.refresh_chart()

    def set_bits_depth(self, depth: int):
        """Définit la profondeur en bits (8, 16...)."""
        self.bits_depth = depth
        self.refresh_chart()

    def set_background(self, color):
        """
        Change la couleur de fond du graphique.
        color : ex. 'k' (noir), 'w' (blanc), '#202020', (r,g,b), (r,g,b,a)
        """
        self.plot.setBackground(color)

    def refresh_chart(self):
        """Recalcule et affiche les histogrammes sous forme de barres."""
        # Empty graphe if no image
        if self.image is None:
            for bar in [self.bar_r, self.bar_g, self.bar_b, self.bar_l]:
                self.plot.removeItem(bar)
            return

        max_val = 2 ** self.bits_depth - 1
        hist_range = (0, max_val)

        # Remove all the data
        for bar in [self.bar_r, self.bar_g, self.bar_b, self.bar_l]:
            self.plot.removeItem(bar)

        image = self.image
        # Fast mode
        if self.image.shape[0] * self.image.shape[1] > 1000000:
            image = resize_image_ratio(image, self.image.shape[0]//4,  self.image.shape[1]//4)


        if image.ndim == 2:
            # Grayscale image
            if self.chk_l.isChecked():
                hist, bins = np.histogram(image, bins=max_val+1, range=hist_range)
                self.bar_l.setOpts(x=bins[:-1], height=hist, width=1)
                self.plot.addItem(self.bar_l)

        elif image.ndim == 3 and image.shape[2] >= 3:
            # RGB image
            if self.chk_r.isChecked():
                hist_r, bins = np.histogram(image[:, :, 0], bins=max_val+1, range=hist_range)
                self.bar_r.setOpts(x=bins[:-1], height=hist_r, width=1)
                self.plot.addItem(self.bar_r)

            if self.chk_g.isChecked():
                hist_g, bins = np.histogram(image[:, :, 1], bins=256, range=hist_range)
                self.bar_g.setOpts(x=bins[:-1], height=hist_g, width=1)
                self.plot.addItem(self.bar_g)

            if self.chk_b.isChecked():
                hist_b, bins = np.histogram(image[:, :, 2], bins=256, range=hist_range)
                self.bar_b.setOpts(x=bins[:-1], height=hist_b, width=1)
                self.plot.addItem(self.bar_b)

            if self.chk_l.isChecked():
                lum = 0.299 * image[:, :, 0] + 0.587 * image[:, :, 1] + 0.114 * image[:, :, 2]
                hist_l, bins = np.histogram(lum, bins=256, range=hist_range)
                self.bar_l.setOpts(x=bins[:-1], height=hist_l, width=1)
                self.plot.addItem(self.bar_l)

class SelectWidget(QWidget):
    """
    Widget including a select list.
    """
    choice_selected = pyqtSignal(str)

    def __init__(self, title: str, values: list, units: str = None):
        """

        :param title:   Title of the widget.
        :param values:  Values of the selection list.
        :param units:   Units of the data.
        """
        super().__init__()
        # Graphical objects
        self.label_title = QLabel(title)
        self.label_title.setStyleSheet(styleH2)
        self.combo_box = QComboBox()
        self.combo_box.addItems(values)
        self.combo_box.currentIndexChanged.connect(self.handle_choice_selected)
        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.label_title, 2)
        layout.addWidget(self.combo_box, 2)
        if units is not None:
            layout.addWidget(units, 1)
        self.setLayout(layout)

    def handle_choice_selected(self):
        """
        Action performed when the colormode choice changed.
        """
        index = self.get_selected_index()
        value = self.get_selected_value()
        self.choice_selected.emit(str(index))

    def get_selected_value(self) -> str:
        """Get the selected value."""
        return self.combo_box.currentText()

    def get_selected_index(self) -> str:
        """Get the index of the selection."""
        return self.combo_box.currentIndex()

    def set_values(self, values: list[str]):
        """Update the list of values.
        :param values: List of values.
        """
        self.combo_box.clear()
        self.combo_box.addItems(values)

    def set_title(self, title: str):
        """
        Change the title of the selection object.
        :param title:   Title of the selection object.
        """
        self.label_title.setText(title)


# --- Exemple d’utilisation ---
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Exemple : label et liste de valeurs
    values = ["Option 1", "Option 2", "Option 3"]
    widget = SelectWidget("Choisissez une option :", values)
    widget.show()

    sys.exit(app.exec())



class LabelWidget(QWidget):
    def __init__(self, title: str, value: str, units: str = None):
        super().__init__()
        widget_w = QWidget()
        layout_w = QHBoxLayout()
        widget_w.setLayout(layout_w)

        self.title = QLabel(title)
        self.value = QLabel(value)
        self.units = QLabel(units)
        self.title.setStyleSheet(styleH2)
        self.value.setStyleSheet(styleH2)
        self.value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.units.setStyleSheet(styleH3)
        layout_w.addWidget(self.title, 2)
        layout_w.addWidget(self.value, 2)
        if units is not None:
            layout_w.addWidget(self.units, 1)
        self.setLayout(layout_w)

    def set_value(self, value):
        """Update widget value."""
        self.value.setText(value)


class ImageDisplayWidget(QWidget):
    def __init__(self, parent=None, bg_color='white', zoom: bool = True):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.scene = QGraphicsScene(self)
        self.graphics_view = QGraphicsView(self.scene)
        self.layout.addWidget(self.graphics_view)
        self.bits_depth = 8
        self.scene.setBackgroundBrush(QColor(bg_color))

    def set_image_from_array(self, pixels_array: np.ndarray, text: str = ''):
        self.scene.clear()
        pixels = pixels_array.copy()
        if pixels is None:
            return
        # Detect if RGB or Grayscale
        if pixels.ndim == 2:
            # Convert image to 8 bits for display
            if self.bits_depth < 8:
                image_8bit = pixels.astype(np.uint8)
            else:
                pow_two = int(self.bits_depth - 8)
                image_8bit = (pixels >> pow_two).astype(np.uint8)
            # Mono
            h, w = image_8bit.shape
            qimage_format = QImage.Format.Format_Grayscale8
        elif pixels.ndim == 3:
            image_8bit = pixels.astype(np.uint8)
            h, w, c = image_8bit.shape
            if c == 3:
                qimage_format = QImage.Format.Format_RGB888
            else:
                raise ValueError(f"Unsupported channel number for RGB: {c}")
        else:
            raise ValueError(f"Unsupported image shape: {image_8bit.shape}")

        # Create QImage
        qimage = QImage(image_8bit.data, w, h, image_8bit.strides[0], qimage_format)
        pixmap = QPixmap.fromImage(qimage)
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(pixmap_item)
        self.graphics_view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

        # Display text if required.
        if text:
            font = QFont('Arial', 12)
            text_item = QGraphicsTextItem(text)
            text_item.setFont(font)
            text_item.setDefaultTextColor(QColor(0, 0, 0))
            text_item.setPos(0, pixmap.height() - 20)
            self.scene.addItem(text_item)

    def set_bits_depth(self, value_depth: int):
        """Set the bits depth of the camera pixels."""
        self.bits_depth = value_depth

