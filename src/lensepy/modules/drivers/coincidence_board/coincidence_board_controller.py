__all__ = ["CoincidenceBoardController"]

import time
from PyQt6.QtWidgets import QWidget
from lensepy.widgets import ImageDisplayWidget

from lensepy.modules.drivers.coincidence_board.coincidence_board_model import NucleoWrapper
from lensepy.appli._app.template_controller import TemplateController


class CoincidenceBoardController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(None)
        self.parent = parent    # main manager
        # Nucleo wrapper
        self.nucleo_wrapper = NucleoWrapper()
        self.parent.variables['nucleo_wrapper'] = self.nucleo_wrapper
        # Graphical layout
        self.top_left = QWidget()
        self.bot_left = QWidget()
        self.top_right = QWidget()
        self.bot_right = QWidget()
        # Setup widgets
        ## List of piezo
        self.boards_list = self.nucleo_wrapper.list_serial_hardware()
        ## If piezo
        if len(self.boards_list) != 0:
            boards_list_display = self._boards_list_display(self.boards_list)
            # self.bot_right.set_boards_list(boards_list_display)

        # Signals
        # self.bot_right.board_connected.connect(self.handle_board_connected)

        # Init view

    def handle_board_connected(self, com):
        """Action performed when nucleo is connected."""
        comm_num = self.nucleo_wrapper.com_list[com]['device']
        self.nucleo_wrapper.set_serial_com(comm_num)
        connected = self.nucleo_wrapper.connect()
        '''
        if connected:
            self.bot_right.set_connected()
        '''

    def handle_image_set(self, number):
        """Action performed when an image is set (opened)."""
        # Open
        config = self.parent.parent.config
        image_ok = False
        if 'img_dir' in config:
            if config['img_dir'] is not None:
                image_path = self._open_image(default_dir=config['img_dir'])
                if image_path is not None:
                    image_array, bits_depth = imread_rgb(image_path)
                    image_ok = True

        # Test if image OK then update view/send button
        if image_ok:
            self.top_right.set_enabled(number)
            self.top_right.set_image_opened(number)
            self.top_right.set_path_to_image(number, image_path)
            image = np.random.randint(0, 256, (300, 700), dtype=np.uint8)
            self.DMD_wrapper.set_image(image_array, int(number))

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

    def _boards_list_display(self, boards_list):
        """
        Prepare the board list for displaying in combobox.
        :boards_list: list of boards list (device, manufacturer, description)
        """
        list_disp = []
        if len(boards_list) != 0:
            for board in boards_list:
                text_disp = f'{board["device"]} | {board["manufacturer"]}'
                list_disp.append(text_disp)
        return list_disp


    def _open_image(self, default_dir: str = '') -> bool:
        """
        Open an image from a file.
        """
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(None, translate('dialog_open_image'),
                                                   default_dir, "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path != '':
            return file_path
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning - No File Loaded")
            dlg.setText("No Image File was loaded...")
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Ok
            )
            dlg.setIcon(QMessageBox.Icon.Warning)
            button = dlg.exec()
            return None

