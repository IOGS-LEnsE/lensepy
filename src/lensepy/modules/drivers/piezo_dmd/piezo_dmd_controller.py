__all__ = ["PiezoDMDController"]

import time
from PyQt6.QtWidgets import QWidget
from lensepy.widgets import ImageDisplayWidget

from lensepy.modules.drivers.piezo_dmd.piezo_dmd_views import *
from lensepy.modules.drivers.piezo_dmd.piezo_dmd_model import DMDWrapper
from lensepy.modules.camera.basler.basler_views import *
from lensepy.appli._app.template_controller import TemplateController


class PiezoDMDController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)
        # DMD wrapper
        self.DMD_wrapper = DMDWrapper()
        # Piezo-Nucleo wrapper
        #self.piezo_wrapper = RGBLedWrapper()
        # Graphical layout
        self.top_left = ImageDisplayWidget()
        self.bot_left = CameraParamsWidget(self)
        self.top_right = DMDParamsView()
        self.bot_right = QWidget()
        # Setup widgets
        ## Camera infos
        camera = self.parent.variables['camera']
        if camera is not None:
            expo_init = camera.get_parameter('ExposureTime')
            self.bot_left.set_exposure_time(expo_init)
            black_level = camera.get_parameter('BlackLevel')
            self.bot_left.set_black_level(black_level)
            fps_init = camera.get_parameter('BslResultingAcquisitionFrameRate')
            fps = np.round(fps_init, 2)
            self.bot_left.label_fps.set_value(str(fps))
        '''
        bits_depth = int(self.parent.variables.get('bits_depth', 8))
        self.top_left.set_bits_depth(bits_depth)
        # Initial Image
        initial_image = self.parent.variables.get('image')
        if initial_image is not None:
            self.top_left.set_image_from_array(initial_image)
            self.update_histogram(initial_image)
            self.update_slices(initial_image)
        '''
        # Signals
        #self.top_left.arduino_connected.connect(self.handle_arduino_connected)
        self.top_right.image_set.connect(self.handle_image_set)
        self.top_right.image_view.connect(self.handle_image_view)
        self.top_right.image_sent.connect(self.handle_image_sent)

        # Init view
        self.top_right.no_image()

    def handle_arduino_connected(self, com):
        """Action performed when arduino is connected."""
        self.wrapper.connect_arduino(com)

    def handle_image_set(self, number):
        """Action performed when an image is set (opened)."""
        # Open

        # Test if image OK then update view/send button
        if True:
            self.top_right.set_enabled(number)
        image = np.random.randint(0, 256, (100, 200), dtype=np.uint8)
        self.DMD_wrapper.set_image(image, int(number))

    def handle_image_view(self, number):
        """Action performed when an image has to be displayed."""
        image = self.DMD_wrapper.get_image(int(number))
        self.top_left.set_image_from_array(image)
        self.top_left.repaint()

    def handle_image_sent(self, number):
        """Action performed when an image has to be sent."""
        image = self.DMD_wrapper.get_image(int(number))
        # Sending...
        self.top_left.set_image_from_array(image)
        self.top_left.repaint()

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