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
from PyQt6 import sip

from lensepy.css import *
from PyQt6.QtCore import Qt, QTimer, QRectF, pyqtSignal, QPointF
from PyQt6.QtGui import QImage, QPixmap, QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import (
    QGraphicsScene, QGraphicsView,
    QVBoxLayout, QGraphicsTextItem, QWidget, QGraphicsLineItem
)


class ImageDisplayWidget(QWidget):
    """Widget d'affichage d'image depuis un array NumPy, avec ajustement automatique à la vue."""

    def __init__(self, parent=None, bg_color='white', zoom: bool = True):
        super().__init__(parent)
        self.bits_depth = 8
        self.zoom = zoom
        self.pixmap_item = None
        self.text_item = None

        # --- Scene & View ---
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(self.view.renderHints() |
                                 QPainter.RenderHint.SmoothPixmapTransform)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scene.setBackgroundBrush(QColor(bg_color))

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        layout.setContentsMargins(0, 0, 0, 0)

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------
    def set_image_from_array(self, pixels_array: np.ndarray, text: str = ''):
        """Affiche une image NumPy (grayscale ou RGB)."""
        if pixels_array is None:
            return
        if sip.isdeleted(self) or sip.isdeleted(self.scene):
            return
        # Delete only pixmap and text.
        if self.pixmap_item:
            self.scene.removeItem(self.pixmap_item)
            self.pixmap_item = None
        if self.text_item:
            self.scene.removeItem(self.text_item)
            self.text_item = None

        qimage = self._convert_array_to_qimage(pixels_array)
        if qimage is None:
            return

        # Crée le pixmap et l'ajoute à la scène
        pixmap = QPixmap.fromImage(qimage)
        self.pixmap_item = self.scene.addPixmap(pixmap)
        self.scene.setSceneRect(QRectF(pixmap.rect()))

        # Ajoute le texte (facultatif)
        if text:
            font = QFont('Arial', 12)
            self.text_item = QGraphicsTextItem(text)
            self.text_item.setFont(font)
            self.text_item.setDefaultTextColor(Qt.GlobalColor.black)
            self.text_item.setPos(5, pixmap.height() - 25)
            self.scene.addItem(self.text_item)

        # Si un point était sélectionné, on redessine la croix
        if hasattr(self, 'selected_point') and self.selected_point:
            self._draw_crosshair(self.selected_point.x(), self.selected_point.y())

        # Ajustement automatique
        QTimer.singleShot(0, self._update_view_fit)

    def set_bits_depth(self, value_depth: int):
        """Définit la profondeur de bits des pixels."""
        self.bits_depth = value_depth

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------
    def _convert_array_to_qimage(self, pixels: np.ndarray) -> QImage | None:
        """Convertit un tableau numpy en QImage compatible avec PyQt."""
        pixels = np.ascontiguousarray(pixels)
        if pixels.ndim == 2:
            # Grayscale
            if self.bits_depth > 8:
                scale = 2 ** (self.bits_depth - 8)
                pixels = (pixels / scale).astype(np.uint8)
            else:
                pixels = pixels.astype(np.uint8)
            h, w = pixels.shape
            return QImage(pixels.data, w, h, pixels.strides[0], QImage.Format.Format_Grayscale8)

        elif pixels.ndim == 3:
            h, w, c = pixels.shape
            if c == 3:
                pixels = pixels.astype(np.uint8)
                return QImage(pixels.data, w, h, pixels.strides[0], QImage.Format.Format_RGB888)
            else:
                raise ValueError(f"Unsupported number of channels: {c}")

        else:
            raise ValueError(f"Unsupported image shape: {pixels.shape}")

    def _update_view_fit(self):
        """
        Adjust the view to the image size, without scrollbars,
        and without enlarging images that are smaller than the view.
        """
        if not self.pixmap_item:
            return

        view_size = self.view.viewport().size()
        img_size = self.scene.sceneRect().size()

        # Readjust image if bigger than the window.
        if img_size.width() > view_size.width() or img_size.height() > view_size.height():
            self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        else:
            # No adjustment if smaller than the window.
            self.view.resetTransform()
            self.view.centerOn(self.pixmap_item)

    def resizeEvent(self, event):
        """Ajuste l'image automatiquement lors du redimensionnement."""
        super().resizeEvent(event)
        self._update_view_fit()


class ImageDisplayWithCrosshair(ImageDisplayWidget):
    """ImageDisplayWidget avec sélection d’un point et affichage d’un réticule (crosshair)."""

    point_selected = pyqtSignal(float, float)

    def __init__(self, parent=None, bg_color='white', zoom: bool = True):
        super().__init__(parent, bg_color, zoom)

        # Couleurs et styles du crosshair
        self.crosshair_pen_h = QPen(QColor(BLUE_IOGS), 2, Qt.PenStyle.SolidLine)
        self.crosshair_pen_v = QPen(QColor(ORANGE_IOGS), 2, Qt.PenStyle.DashLine)

        # Lignes du crosshair
        self.h_line = None
        self.v_line = None

        # État du crosshair
        self.selected_point = None
        self.dragging = False

        # Active la détection de clics et mouvements sur la scène
        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------
    def eventFilter(self, obj, event):
        if obj is self.view.viewport():
            if event.type() == event.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                self.dragging = True
                self._update_point(event)
            elif event.type() == event.Type.MouseMove and self.dragging:
                self._update_point(event)
            elif event.type() == event.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
                self.dragging = False
        return super().eventFilter(obj, event)

    # ------------------------------------------------------------------
    # Crosshair logic
    # ------------------------------------------------------------------
    def _update_point(self, event):
        """Met à jour la position du point sélectionné lors du clic ou du drag."""
        pos = self.view.mapToScene(event.pos())
        x, y = pos.x(), pos.y()
        self.selected_point = QPointF(x, y)
        self._draw_crosshair(x, y)
        self.point_selected.emit(x, y)

    def _draw_crosshair(self, x, y):
        """Dessine ou déplace les lignes du crosshair."""
        scene_rect = self.scene.sceneRect()

        # Si les lignes n'existent pas ou ont été supprimées, on les recrée
        if not self.h_line or self.h_line.scene() is None:
            self.h_line = QGraphicsLineItem()
            self.h_line.setPen(self.crosshair_pen_h)
            self.scene.addItem(self.h_line)

        if not self.v_line or self.v_line.scene() is None:
            self.v_line = QGraphicsLineItem()
            self.v_line.setPen(self.crosshair_pen_v)
            self.scene.addItem(self.v_line)

        # Met à jour la position des lignes
        self.h_line.setLine(scene_rect.left(), y, scene_rect.right(), y)
        self.v_line.setLine(x, scene_rect.top(), x, scene_rect.bottom())

    def set_image_from_array(self, pixels_array: np.ndarray, text: str = ''):
        """Affiche une image NumPy et conserve le crosshair existant."""
        # Sauvegarde la position actuelle du crosshair
        saved_point = self.selected_point

        # Appel au parent (efface et réaffiche l’image)
        super().set_image_from_array(pixels_array, text)

        # --- Correction : les items ont été détruits, on oublie les anciens pointeurs Python ---
        self.h_line = None
        self.v_line = None

        # Réaffiche le crosshair si un point avait été sélectionné
        if saved_point is not None:
            x, y = saved_point.x(), saved_point.y()
            self.selected_point = saved_point
            self._draw_crosshair(x, y)




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