import os
from pathlib import Path

import numpy as np
from PyQt6.QtCore import QThread

from lensepy import translate
from lensepy.widgets import HistoStatsWidget
from lensepy.css import *
from lensepy.appli._app.template_controller import TemplateController, ImageLive
from lensepy.widgets import XYMultiChartWidget, ImageDisplayWidget
from lensepy.modules.time_camera.time_camera_views import TimeOptionsWidget
from lensepy.widgets import CameraParamsWidget


class TimeCameraController(TemplateController):
    """Controller for camera acquisition."""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Attributes initialization
        self.img_dir = self._get_image_dir(self.parent.parent.config['img_dir'])
        self.thread = None
        self.worker = None

        # Widgets
        self.top_left = ImageDisplayWidget()
        self.bot_left = HistoStatsWidget()
        self.bot_right = TimeOptionsWidget()
        self.bot_right.set_img_dir(self.img_dir)
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
        # Camera infos
        camera = self.parent.variables['camera']
        if camera is not None:
            expo_init = camera.get_parameter('ExposureTime')
            self.bot_right.set_exposure_time(expo_init)
            black_level = camera.get_parameter('BlackLevel')
            self.bot_right.set_black_level(black_level)
            fps_init = camera.get_parameter('BslResultingAcquisitionFrameRate')
            fps = np.round(fps_init, 2)
            self.bot_right.set_frame_rate(fps)
            self.top_right.set_title(translate('image_time_xy_title'))
        # Start live acquisition
        self.start_live()

    def start_live(self):
        """Start live acquisition with camera."""
        self.thread = QThread()
        self.worker = ImageLive(self)
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
        # Update histogram
        self.update_histogram(image)
        # Store new image.
        self.parent.variables['image'] = image.copy()

    def handle_exposure_changed(self, value):
        """
        Action performed when the color mode changed.
        """
        camera = self.parent.variables["camera"]
        if camera is not None:
            # Stop live safely
            self.stop_live()
            # Close camera
            camera.close()
            # Read available formats
            camera.set_parameter('ExposureTime', value)
            camera.initial_params['ExposureTime'] = value
            self.bot_right.update_infos()
            # Restart live
            camera.open()
            self.start_live()

    def handle_black_level_changed(self, value):
        """
        Action performed when the black level changed.
        """
        camera = self.parent.variables["camera"]
        if camera is not None:
            # Stop live safely
            self.stop_live()
            # Close camera
            camera.close()
            # Update information
            camera.set_parameter('BlackLevel', value)
            camera.initial_params['BlackLevel'] = value
            self.bot_right.update_infos()
            # Restart live
            camera.open()
            self.start_live()

    # Histogram
    def update_histogram(self, image):
        """
        Update histogram value from image.
        :param image:   Numpy array containing the new image.
        """
        if image is not None:
            self.bot_left.set_image(image)

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

    def _get_image_dir(self, filepath):
        if filepath is None:
            return ''
        else:
            # Detect if % in filepath
            if '%USER' in filepath:
                new_filepath = filepath.split('%')
                new_filepath = f'{Path.home()}/{new_filepath[2]}'
                return new_filepath
            else:
                return filepath