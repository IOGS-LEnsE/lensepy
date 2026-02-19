__all__ = ["PiezoDMDController"]

import time
from PyQt6.QtWidgets import QWidget
from lensepy.widgets import ImageDisplayWidget

from lensepy.modules.drivers.piezo_dmd.piezo_dmd_views import *
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
        #self.DMD_wrapper = RGBLedWrapper()
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

    def handle_arduino_connected(self, com):
        """Action performed when arduino is connected."""
        self.wrapper.connect_arduino(com)



