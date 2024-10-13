# -*- coding: utf-8 -*-
"""*widget_image_histogram* file.

*widget_image_histogram* file that contains :class::ImageHistogramWidget

.. module:: ImageHistogramWidget
   :synopsis: class to display the histogram in PyQt6 of an image (requires pyqtGraph).

.. note:: LEnsE - Institut d'Optique - version 0.1

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>
"""

# Standard Libraries
import numpy as np
import sys

# Third pary imports
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from pyqtgraph import PlotWidget, BarGraphItem
if __name__ == '__main__':
    from widget_histogram import HistogramWidget
else:
    from lensepy.pyqt6.widget_histogram import HistogramWidget
from lensepy.css import *
from lensepy.images.conversion import resize_image_ratio


class ImageHistogramWidget(HistogramWidget):
    """Create a Widget with a histogram.

    Widget used to display a histogram of an image.
    Children of HistogramWidget.
    """

    def __init__(self, name: str = '', info:bool = True) -> None:
        """Initialize the histogram widget.
        """
        super().__init__(name, info)
        self.bit_depth = 8
        self.bins = np.linspace(0, 2**self.bit_depth, 2**self.bit_depth+1)

    def set_bit_depth(self, bit_depth: int = 8):
        """Set the bit depth of a pixel."""
        self.bit_depth = bit_depth
        self.bins = np.linspace(0, 2**self.bit_depth, 2**self.bit_depth+1)

    def set_image(self, image: np.ndarray, fast_mode: bool = False, black_mode:bool = False, log_mode: bool = False) -> None:
        """Set an image and the bit depth of a pixel.

        :param image: data of the image.
        :type image: np.ndarray
        :param fast_mode: if True, image is resized to accelerate the histogram calculation
        :type fast_mode: bool
        """
        if fast_mode:
            image = resize_image_ratio(image, image.shape[0]//4,  image.shape[1]//4)
        super().set_data(image, self.bins, black_mode=black_mode, log_mode=log_mode)
        super().refresh_chart()

if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication


    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle("Widget Slider test")
            self.setGeometry(300, 300, 700, 400)

            self.central_widget = QWidget()
            self.layout = QVBoxLayout()

            self.histo_widget = ImageHistogramWidget('Histogram Test')
            self.histo_widget.set_information('This is a test')
            self.layout.addWidget(self.histo_widget)

            my_image = np.random.randint(0, 4095, (800, 600), dtype=np.uint16)
            #self.histo_widget.set_y_axis_limit(500)
            self.histo_widget.set_background('white')
            self.histo_widget.set_image(my_image, nb_of_bits=12)

            self.central_widget.setLayout(self.layout)
            self.setCentralWidget(self.central_widget)


    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
