"""
image_display_widget.py
=======================

PyQt6 widget for displaying images from numpy arrays in a QGraphicsView.
Supports both grayscale and RGB images, with optional text overlay and
customizable bits depth.

Features
--------

- Supports grayscale and RGB images
- Converts higher bit-depth images to 8-bit for display
- Optional overlay text
- Maintains aspect ratio in QGraphicsView
- Customizable background color

Usage Example
-------------

.. code-block:: python

    import sys
    import numpy as np
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = ImageDisplayWidget(bg_color='white')

    # Create a test RGB image 256x256
    test_image = np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8)
    widget.set_image_from_array(test_image, text="Test Image")
    widget.show()
    sys.exit(app.exec())


Author : Julien VILLEMEJANE / LEnsE - IOGS
Date   : 2025-10-09
"""

import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap, QColor, QFont
from PyQt6.QtWidgets import (
    QGraphicsPixmapItem, QGraphicsScene, QGraphicsView,
    QVBoxLayout, QGraphicsTextItem, QWidget
)


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


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = ImageDisplayWidget(bg_color='white')

    # Create a test RGB image 256x256
    test_image = np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8)
    widget.set_image_from_array(test_image, text="Test Image")
    widget.show()
    sys.exit(app.exec())