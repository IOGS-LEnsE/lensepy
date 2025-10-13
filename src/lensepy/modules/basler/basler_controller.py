import time
from PyQt6.QtCore import QObject, QThread
from lensepy.appli._app.template_controller import TemplateController
from lensepy.modules.basler.basler_views import *
from lensepy.modules.basler.basler_models import *
from lensepy.widgets import *


class BaslerController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """
        :param parent:
        """
        super().__init__(parent)
        # Attributes initialization
        self.camera_connected = False       # Camera is connected
        self.thread = None
        self.worker = None
        self.colormode = []
        self.colormode_bits_depth = []
        # Widgets
        self.top_left = ImageDisplayWidget()
        self.bot_left = HistogramWidget()
        self.bot_right = CameraParamsWidget(self)
        self.top_right = CameraInfosWidget(self)
        # Check if camera is connected
        self.init_camera()
        # Camera infos
        camera = self.parent.variables['camera']
        if camera is not None:
            expo_init = camera.get_parameter('ExposureTime')
            self.bot_right.slider_expo.set_value(expo_init)
            fps_init = camera.get_parameter('BslResultingAcquisitionFrameRate')
            self.bot_right.label_fps.set_value(str(fps_init))

    def init_view(self):
        """
        Update graphical objects of the interface.
        """
        # Update view
        if self.parent.variables['camera'] is not None:
            super().init_view()
            self.set_color_mode()
            self.top_right.label_color_mode.set_values(self.colormode)
            self.update_color_mode()
            # Setup widgets
            self.bot_left.set_background('white')
            self.top_right.update_infos()
            # Init widgets
            if self.parent.variables['bits_depth'] is not None:
                self.top_left.set_bits_depth(int(self.parent.variables['bits_depth']))
                self.bot_left.set_bits_depth(int(self.parent.variables['bits_depth']))
            else:
                self.bot_left.set_bits_depth(8)
            if self.parent.variables['image'] is not None:
                self.top_left.set_image_from_array(self.parent.variables['image'])
                self.bot_left.set_image(self.parent.variables['image'])
            self.bot_left.refresh_chart()
            # Signals
            self.top_right.color_mode_changed.connect(self.handle_color_mode_changed)
            self.bot_right.exposure_time_changed.connect(self.handle_exposure_time_changed)
            self.start_live()
        else:
            self.top_left = QLabel('No Camera is connected. \n'
                                   'Connect a camera first.\n'
                                   'Then restart the application.')
            self.top_left.setStyleSheet(styleH2)
            self.bot_left = QWidget()
            self.top_right = QWidget()
            self.bot_right = QWidget()
            super().init_view()

    def init_camera(self):
        """
        Initialize the camera.
        """
        camera = self.parent.variables["camera"]
        # Check if a camera is already connected
        if camera is None:
            # Init Camera
            self.parent.variables["camera"] = BaslerCamera()
            self.camera_connected = self.parent.variables["camera"].find_first_camera()
            if self.camera_connected is False:
                self.parent.variables["camera"] = None
            else:
                self.parent.variables["first_connexion"] = 'Yes'
        else:
            self.camera_connected = True
            self.parent.variables["first_connexion"] = 'No'

    def set_color_mode(self):
        # Get color mode list
        colormode_get = self.parent.xml_app.get_sub_parameter('camera','colormode')
        colormode_get = colormode_get.split(',')
        for colormode in colormode_get:
            colormode_v = colormode.split(':')
            self.colormode.append(colormode_v[0])
            self.colormode_bits_depth.append(int(colormode_v[1]))

    def update_color_mode(self):
        camera = self.parent.variables["camera"]
        # Update to first mode if first connection
        pix_format = camera.get_parameter('PixelFormat')
        if 'first_connexion' in self.parent.variables:
            if self.parent.variables['first_connexion'] == 'Yes':
                first_mode_color = self.colormode[0]
                camera.open()
                camera.set_parameter("PixelFormat", first_mode_color)
                camera.initial_params["PixelFormat"] = first_mode_color
                camera.close()
                first_bits_depth = self.colormode_bits_depth[0]
                self.parent.variables["bits_depth"] = first_bits_depth
            else:
                idx = self.colormode.index(pix_format)
                self.top_right.label_color_mode.set_choice(idx)
                new_bits_depth = self.colormode_bits_depth[idx]
                self.parent.variables["bits_depth"] = new_bits_depth

    def start_live(self):
        """
        Start live acquisition from camera.
        """
        if self.camera_connected:
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
        """
        Stop live mode, i.e. continuous image acquisition.
        """
        if self.worker is not None:
            # Arrêter le worker
            self.worker._running = False

            # Attendre la fin du thread
            if self.thread is not None:
                self.thread.quit()
                self.thread.wait()  # bloque jusqu'à la fin

            # Supprimer les références
            self.worker = None
            self.thread = None

    def handle_image_ready(self, image: np.ndarray):
        """
        Thread-safe GUI updates
        :param image:   Numpy array containing new image.
        """
        # Update Image
        self.top_left.set_image_from_array(image)
        # Update Histo
        self.bot_left.set_image(image, checked=False)
        # Store new image.
        self.parent.variables['image'] = image.copy()

    def display_image(self, image: np.ndarray):
        """
        Display the image given as a numpy array.
        :param image:   numpy array containing the data.
        :return:
        """
        self.top_left.set_image_from_array(image)

    def handle_exposure_time_changed(self, value):
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
            # Restart live
            camera.open()
            self.start_live()

    def handle_color_mode_changed(self, event):
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
            available_formats = []
            try:
                if camera.camera_device is not None:
                    camera.open()
                    available_formats = list(camera.camera_device.PixelFormat.Symbolics)
                    camera.close()
            except Exception as e:
                print(f"Unable to read PixelFormat.Symbolics: {e}")
            # Select new format
            idx = int(event)
            new_format = self.colormode[idx] if idx < len(self.colormode) else None

            if new_format is None:
                return
            if new_format in available_formats:
                camera.open()
                camera.set_parameter("PixelFormat", new_format)
                camera.initial_params["PixelFormat"] = new_format
                camera.close()
            # Change bits depth
            self.parent.variables['bits_depth'] = self.colormode_bits_depth[idx]
            self.bot_left.set_bits_depth(int(self.parent.variables['bits_depth']))
            self.top_left.set_bits_depth(int(self.parent.variables['bits_depth']))
            if 'Bayer' in new_format:
                self.bot_left.reinit_checkbox('RGB')
            elif 'Mono' in new_format:
                self.bot_left.reinit_checkbox('Gray')
            # Restart live
            camera.open()
            self.start_live()

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
            time.sleep(0.01)

        camera.camera_acquiring = False
        camera.close()
        self.finished.emit()

    def stop(self):
        self._running = False
