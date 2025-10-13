import time
import numpy as np
from PyQt6 import sip
from PyQt6.QtCore import QObject, QThread, pyqtSignal

from lensepy import translate
from lensepy.css import *
from lensepy.appli._app.template_controller import TemplateController
from lensepy.widgets import ImageDisplayWithCrosshair, HistogramWidget, XYMultiChartWidget
from lensepy.modules.spatial_camera.spatial_camera_views import CameraParamsWidget


class SpatialCameraController(TemplateController):
    """Controller for camera acquisition."""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Attributes initialization
        self.x_cross = None
        self.y_cross = None
        self.thread = None
        self.worker = None

        # Widgets
        self.top_left = ImageDisplayWithCrosshair()
        self.bot_left = HistogramWidget()
        self.bot_right = CameraParamsWidget(self)
        self.top_right = XYMultiChartWidget()
        self.bot_left.set_background('white')
        # Bits depth
        bits_depth = int(self.parent.variables.get('bits_depth', 8))
        self.top_left.set_bits_depth(bits_depth)
        self.bot_left.set_bits_depth(bits_depth)

        # Initial Image
        initial_image = self.parent.variables.get('image')
        if initial_image is not None:
            self.top_left.set_image_from_array(initial_image)
            self.update_histogram(initial_image)
            self.update_slices(initial_image)
        # Crosshair
        self.top_left.point_selected.connect(self.handle_xy_changed)
        # Start live acquisition
        self.start_live()

    def start_live(self):
        """Start live acquisition with camera."""
        self.thread = QThread()
        self.worker = ImageLive(self, fps=30)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.image_ready.connect(self.handle_image_ready)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def stop_live(self):
        """Stop live acquisition."""
        if self.worker:
            self.worker.stop()
            if self.thread:
                self.thread.quit()
                self.thread.wait()
            self.worker = None
            self.thread = None

    def handle_image_ready(self, image: np.ndarray):
        """
        Thread-safe GUI updates
        :param image:   Numpy array containing new image.
        """
        self.top_left.set_image_from_array(image)
        # Update Slices and histogram not each time
        self.update_histogram(image)
        self.update_slices(image)
        # Store new image.
        self.parent.variables['image'] = image.copy()

    # Histogram & slices
    def update_histogram(self, image):
        """
        Update histogram value from image.
        :param image:   Numpy array containing the new image.
        """
        if image is not None:
            self.bot_left.set_image(image, checked=False)
            self.bot_left.refresh_chart()

    def handle_xy_changed(self, x, y):
        """
        Action performed when a crosshair is selected.
        :param x: X coordinate.
        :param y: Y coordinate.
        """
        self.x_cross = x
        self.y_cross = y
        image = self.parent.variables.get('image')
        if image is not None:
            self.update_slices(image)

    def update_slices(self, image):
        """
        Update slice values from image.
        :param image:   Numpy array containing the new image.
        """
        if self.x_cross is None or self.y_cross is None or image is None:
            return

        # Détection du type d'image et conversion en grayscale/luminance si nécessaire
        if image.ndim == 2:  # grayscale
            gray_image = image
        elif image.ndim == 3 and image.shape[2] == 3:  # RGB
            gray_image = 0.299 * image[:, :, 0] + 0.587 * image[:, :, 1] + 0.114 * image[:, :, 2]
        else:
            raise ValueError("Image format non supporté")

        x_idx, y_idx = int(self.x_cross), int(self.y_cross)
        x_data = gray_image[y_idx, :]
        y_data = gray_image[:, x_idx]

        xx = np.linspace(1, len(x_data), len(x_data))
        yy = np.linspace(1, len(y_data), len(y_data))
        X_x = [xx, yy]
        Y_y = [x_data, y_data]

        self.top_right.set_data(X_x, Y_y, y_names=[translate('horizontal'), translate('vertical')],
                                x_label='position', y_label='intensity')
        self.top_right.refresh_chart()
        self.top_right.set_information(
            f'Mean H = {np.mean(x_data):.1f} / Min = {np.min(x_data):.1f} / Max = {np.max(x_data):.1f} [] '
            f'Mean V = {np.mean(y_data):.1f} / Min = {np.min(y_data):.1f} / Max = {np.max(y_data):.1f}')


    def cleanup(self):
        """
        Stop the camera cleanly and release resources.
        """
        self.stop_live()
        camera = self.parent.variables["camera"]
        if camera is not None:
            if getattr(camera, "is_open", False):
                camera.close()
            camera.camera_acquiring = False
        self.worker = None
        self.thread = None


class ImageLive(QObject):
    """
    Worker for image acquisition.
    Based on threads.
    """
    image_ready = pyqtSignal(np.ndarray)
    finished = pyqtSignal()

    def __init__(self, controller, fps=30):
        super().__init__()
        self.controller = controller
        self._running = False
        self.fps = fps

    def run(self):
        camera = self.controller.parent.variables.get("camera")
        if camera is None:
            return

        self._running = True
        camera.open()
        camera.camera_acquiring = True

        while self._running:
            image = camera.get_image()
            if image is not None and not sip.isdeleted(self):
                self.image_ready.emit(image)
            time.sleep(0.001)

        camera.camera_acquiring = False
        camera.close()
        self.finished.emit()

    def stop(self):
        self._running = False
