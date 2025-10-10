import cv2
import numpy as np
from lensepy import translate
from lensepy.css import *
from lensepy.utils import make_hline
from lensepy.widgets import LabelWidget
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QLabel
)


class FFTImagesParamsWidget(QWidget):
    """
    Widget to display image infos.
    """
    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent
        layout = QVBoxLayout()

        self.image = None

        label = QLabel(translate('fft_image_params_title'))
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




if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from matplotlib import pyplot as plt
    app = QApplication(sys.argv)
    image = cv2.imread('./robot.jpg')
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    w = FFTImagesParamsWidget()
    w.resize(800, 600)
    w.show()

    # Exemple : image RGB aléatoire


    sys.exit(app.exec())
