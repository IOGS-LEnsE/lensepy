import time
from PyQt6.QtCore import QObject, QThread
from lensepy.appli._app.template_controller import TemplateController, ImageLive
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
        self.roi_coords = []
        self.roi_coords_old = []
        self.camera_range = [0, 0, 0, 0]
        # Widgets
        self.top_left = RectangleDisplayWidget()
        self.bot_left = HistogramWidget()
        self.top_right = CameraInfosWidget(self)
        self.bot_right = CameraParamsWidget(self)
        # Widgets setup and signals
        self.top_left.set_enabled(False)
        self.top_left.rectangle_changed.connect(self.handle_rect_changed)
        self.top_right.roi_checked.connect(self.handle_roi_checked)
        self.top_right.roi_changed.connect(self.handle_rect_changed)
        self.top_right.roi_centered.connect(self.handle_roi_centered)
        self.top_right.roi_reset.connect(self.handle_roi_reset)
        # Check if camera is connected
        self.init_camera()
        self.top_right.set_roi([0, 10, 10, 50])
        # Camera infos
        camera = self.parent.variables['camera']
        if camera is not None:
            expo_init = camera.get_parameter('ExposureTime')
            self.bot_right.slider_expo.set_value(expo_init)
            fps_init = camera.get_parameter('BslResultingAcquisitionFrameRate')
            fps = np.round(fps_init, 2)
            self.bot_right.label_fps.set_value(str(fps))

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
            self.bot_right.black_level_changed.connect(self.handle_black_level_changed)
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
                camera = self.parent.variables["camera"]
                self.parent.variables["first_connexion"] = 'Yes'
                self.camera_range = [0, 0, camera.get_parameter('WidthMax'), camera.get_parameter('HeightMax')]
                self.roi_coords = self.camera_range.copy()
                self.roi_coords_old = self.camera_range.copy()
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
            self.bot_right.update_infos()
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
            # Read available formats
            camera.set_parameter('BlackLevel', value)
            camera.initial_params['BlackLevel'] = value
            self.bot_right.update_infos()
            # Restart live
            camera.open()
            self.start_live()

    def handle_rect_changed(self, coords):
        """Action performed when a new rectangle has been drawn."""
        coords = [int(x) for x in coords]
        self.roi_coords = self.check_order(coords)

        print(f'Controller / handle_rect_changed: {self.roi_coords}')
        if self.check_roi_range(self.roi_coords):

            # Draw rectangle ?

            self.top_right.set_roi(self.roi_coords)
        else:
            # Reset old values
            self.roi_coords = self.roi_coords_old
        # Update Top_Right widget
        self.top_right.set_roi(self.roi_coords)
        self.top_left.draw_rectangle(self.roi_coords)


    def check_order(self, coords: list):
        """
        Check coordinates order.
        :param coords:  x0, y0, x1, y1 coordinates.
        """
        x0, y0, x1, y1 = coords
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        coords = [x0, y0, x1, y1]
        return coords

    def check_roi_range(self, coords: list):
        """
        Check ROI range, if in the camera range.
        :param coords: ROI coordinates.
        """
        if (coords[0] < self.camera_range[0] or coords[2] > self.camera_range[2]
                or coords[1] < self.camera_range[1] or coords[3] > self.camera_range[3]):
            return False
        else:
            return True

    def handle_roi_centered(self, coords: list):
        """
        Recenter the ROI.
        :param coords:  x0, y0, x1, y1 coordinates.
        """
        new_coords = self.check_order(coords)
        new_w = new_coords[2] - new_coords[0]
        new_x0 = (self.camera_range[2] - self.camera_range[0]) // 2 - new_w // 2
        new_x1 = (self.camera_range[2] - self.camera_range[0]) // 2 + new_w // 2
        new_h = new_coords[3] - new_coords[1]
        new_y0 = (self.camera_range[3] - self.camera_range[1]) // 2 - new_h // 2
        new_y1 = (self.camera_range[3] - self.camera_range[1]) // 2 + new_h // 2
        print(f'New coords : {[new_x0, new_y0, new_x1, new_y1]}')
        if self.check_roi_range([new_x0, new_y0, new_x1, new_y1]):
            self.roi_coords = [new_x0, new_y0, new_x1, new_y1]
            self.top_right.set_roi(self.roi_coords)
            self.top_left.draw_rectangle(self.roi_coords)
        else:
            self.top_right.set_roi(self.roi_coords)

    def handle_roi_checked(self, value: bool):
        """Action performed when a new ROI has been selected.
        :param value:   True if ROI is checked.
        """
        if not value:
            # Reinit ROI to maximum camera range
            self.roi_coords_old = self.roi_coords.copy()
            self.roi_coords = self.camera_range.copy()
            self.top_right.set_roi(self.roi_coords)
            # Stop access to drawing on Image
            self.top_left.set_enabled(False)
        else:
            # Restore old ROI
            self.roi_coords = self.roi_coords_old
            self.top_right.set_roi(self.roi_coords)
            # Start access to drawing on Image
            self.top_left.set_enabled(True)
            self.top_left.draw_rectangle(self.roi_coords)
        # Update ROI Selection Widget

    def handle_roi_reset(self):
        self.roi_coords = self.camera_range.copy()
        print(f'Reset ROI: {self.roi_coords}')
        self.top_right.set_roi(self.roi_coords)
        self.top_left.draw_rectangle(self.roi_coords)

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


