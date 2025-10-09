import os
import cv2
import numpy as np
import importlib
from lensepy import translate
from lensepy.css import *
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox,
    QWidget, QLabel, QPushButton, QFrame, QCheckBox, QSizePolicy
)
from lensepy.images.conversion import resize_image_ratio
import pyqtgraph as pg


class ImagesOpeningWidget(QWidget):
    """
    Widget to display image opening options.
    """

    image_opened = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent    # Controller
        layout = QVBoxLayout()

        h_line = QFrame()
        h_line.setFrameShape(QFrame.Shape.HLine)  # Trait horizontal
        h_line.setFrameShadow(QFrame.Shadow.Sunken)  # Effet "enfoncé" (optionnel)
        layout.addWidget(h_line)

        label = QLabel(translate('image_opening_dialog'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.open_button = QPushButton(translate('image_opening_button'))
        self.open_button.setStyleSheet(unactived_button)
        self.open_button.setFixedHeight(BUTTON_HEIGHT)
        self.open_button.clicked.connect(self.handle_opening)
        layout.addWidget(self.open_button)

        layout.addStretch()
        self.setLayout(layout)

    def handle_opening(self):
        sender = self.sender()
        if sender == self.open_button:
            self.open_button.setStyleSheet(actived_button)

            module_path = self.parent.parent.xml_app.get_module_parameter('images', 'imgdir')
            print(module_path)
            module = importlib.import_module(module_path)
            xml_path = os.path.dirname(module.__file__)
            print(f'Path = {test}')
            im_ok = self.open_image()
            if im_ok:
                self.open_button.setStyleSheet(unactived_button)

    def open_image(self, default_dir: str = '') -> bool:
        """
        Open an image from a file.
        """
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, translate('dialog_open_image'),
                                                   default_dir, "Images (*.png *.jpg *.jpeg)")
        if file_path != '':
            image_array, bits_depth = imread_rgb(file_path)
            self.parent.get_variables()['image'] = image_array
            self.parent.get_variables()['bits_depth'] = bits_depth
            self.image_opened.emit('image_opened')
            return True
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning - No File Loaded")
            dlg.setText("No Image File was loaded...")
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Ok
            )
            dlg.setIcon(QMessageBox.Icon.Warning)
            button = dlg.exec()
            return False


class ImagesInfosWidget(QWidget):
    """
    Widget to display image infos.
    """
    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent
        layout = QVBoxLayout()

        self.image = None

        label = QLabel(translate('image_infos_title'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        layout.addWidget(make_hline())

        self.label_w = LabelWidget(translate("image_infos_label_w"), '', 'pixels')
        layout.addWidget(self.label_w)
        self.label_h = LabelWidget(translate("image_infos_label_h"), '', 'pixels')
        layout.addWidget(self.label_h)

        layout.addWidget(make_hline())

        self.label_type = LabelWidget(translate("image_infos_label_type"), '', '')
        layout.addWidget(self.label_type)

        layout.addStretch()
        self.setLayout(layout)
        self.hide()

    def update_infos(self, image: np.ndarray):
        """
        Update information from image.
        :param image:   Displayed image.
        """
        self.image = image
        if self.image is not None:
            self.show()
            self.label_w.set_value(f'{self.image.shape[1]}')
            self.label_h.set_value(f'{self.image.shape[0]}')
            if self.image.ndim == 2:
                self.label_type.set_value(f'GrayScale')
            else:
                self.label_type.set_value(f'RGB')
        else:
            self.hide()




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

    def set_image(self, img: np.ndarray):
        """Définit l'image (numpy array, 2D pour gris ou 3D pour RGB)."""
        self.image = img
        if self.image.ndim == 2:
            # Grayscale image
            for chk in [self.chk_r, self.chk_g, self.chk_b]:
                chk.setEnabled(False)
                chk.setChecked(False)
            self.chk_l.setEnabled(False)
            self.chk_l.setChecked(True)
        elif self.image.ndim == 3:
            # RGB image
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
                hist, bins = np.histogram(image, bins=256, range=hist_range)
                self.bar_l.setOpts(x=bins[:-1], height=hist, width=1)
                self.plot.addItem(self.bar_l)

        elif image.ndim == 3 and image.shape[2] >= 3:
            # RGB image
            if self.chk_r.isChecked():
                hist_r, bins = np.histogram(image[:, :, 0], bins=256, range=hist_range)
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

class LabelWidget(QWidget):
    def __init__(self, title: str, value: str, units: str):
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
        layout_w.addWidget(self.units, 1)
        self.setLayout(layout_w)

    def set_value(self, value):
        """Update widget value."""
        self.value.setText(value)

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = HistogramWidget()
    w.resize(800, 600)
    w.show()

    # Exemple : image RGB aléatoire
    img = (np.random.rand(256, 256, 3) * 255).astype(np.uint8)
    w.set_image(img)
    w.set_background('white')
    w.set_bits_depth(8)

    sys.exit(app.exec())
