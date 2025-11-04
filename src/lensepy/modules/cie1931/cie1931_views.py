import sys
from PyQt6 import QtWidgets
import matplotlib
matplotlib.use("QtAgg")  # choisira Qt6 si PyQt6 est installé
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import colour

class CIE1931MatplotlibWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        fig, ax = plt.subplots()
        colour.plotting.plot_chromaticity_diagram_CIE1931(
            show=False, axes=ax,
            show_diagram_colours=True,
            show_spectral_locus=True,
            show_colourspace_diagram=False
        )
        #colour.plotting.temperature.plot_planckian_locus(axes=ax, show=False)
        self.canvas = FigureCanvas(fig)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        ax.plot(0.33, 0.33, 'kD', label="D65")
        ax.plot(0.2, 0.7, 'kx', label="Test 1")
        ax.plot(0.4, 0.2, 'kx', label="Test 2")
        ax.legend(loc="upper right")
        ax.set_xlim(-0.1, 0.8)
        ax.set_ylim(0, 0.9)
        self.canvas.draw()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = CIE1931MatplotlibWidget()
    win.setWindowTitle("Diagramme CIE 1931")
    win.resize(800, 700)
    win.show()
    sys.exit(app.exec())
