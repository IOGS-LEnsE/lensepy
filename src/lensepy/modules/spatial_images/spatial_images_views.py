import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit
)
from pyqtgraph import PlotWidget, mkPen, mkBrush
from PyQt6.QtCore import Qt, pyqtSignal, QPointF
from PyQt6.QtGui import QPen, QColor
from PyQt6.QtWidgets import QGraphicsLineItem
from lensepy.css import *
from lensepy.widgets import ImageDisplayWidget


class ImageDisplayWithCrosshair(ImageDisplayWidget):
    """ImageDisplayWidget avec sélection d’un point et affichage d’un réticule (croix)."""

    point_selected = pyqtSignal(float, float)  # (x, y) dans l'image

    def __init__(self, parent=None, bg_color='white', zoom: bool = True):
        super().__init__(parent, bg_color, zoom)
        self.crosshair_color = QColor(255, 0, 0)  # rouge
        self.crosshair_pen = QPen(self.crosshair_color, 1, Qt.PenStyle.SolidLine)
        self.h_line = None
        self.v_line = None
        self.selected_point = None
        self.dragging = False  # nouveau flag pour suivre le drag

        # Active la détection de clics et mouvements sur la scène
        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)

    # ----------------------------------------------------------------------
    # Event handling : on intercepte les clics et mouvements sur la vue
    # ----------------------------------------------------------------------
    def eventFilter(self, obj, event):
        if obj is self.view.viewport():
            if event.type() == event.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                self.dragging = True
                self._update_point(event)
            elif event.type() == event.Type.MouseMove and self.dragging:
                self._update_point(event)
            elif event.type() == event.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
                self.dragging = False
        return super().eventFilter(obj, event)

    def _update_point(self, event):
        """Convertit la position du curseur en coordonnées scène et met à jour la croix."""
        pos = self.view.mapToScene(event.pos())
        x, y = pos.x(), pos.y()
        self.selected_point = QPointF(x, y)
        self._draw_crosshair(x, y)
        self.point_selected.emit(x, y)

    # ----------------------------------------------------------------------
    # Crosshair drawing
    # ----------------------------------------------------------------------
    def _draw_crosshair(self, x, y):
        """Dessine ou met à jour les lignes du réticule."""
        scene_rect = self.scene.sceneRect()

        # Supprime les anciennes lignes si elles existent
        if self.h_line:
            self.scene.removeItem(self.h_line)
        if self.v_line:
            self.scene.removeItem(self.v_line)

        # Crée les nouvelles lignes
        self.h_line = QGraphicsLineItem(scene_rect.left(), y, scene_rect.right(), y)
        self.v_line = QGraphicsLineItem(x, scene_rect.top(), x, scene_rect.bottom())

        for line in (self.h_line, self.v_line):
            line.setPen(self.crosshair_pen)
            self.scene.addItem(line)


class SliderBloc(QWidget):
    """
    Slider block combining a numeric input and a horizontal slider.
    Emits the current value whenever it changes.
    """

    slider_changed = pyqtSignal(float)

    def __init__(self, name: str, unit: str, min_value: float, max_value: float,
                 integer: bool = False) -> None:
        super().__init__()

        self.integer = integer
        self.unit = unit
        self.min_value = min_value
        self.max_value = max_value
        self.ratio = 1 if integer else 100
        self.value = round(min_value + (max_value - min_value) / 3, 2)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # --- First line: label + input + unit ---
        self._init_value_line(name)

        # --- Second line: slider + min/max labels ---
        self._init_slider_line()

        self.update_block()

    # ----------------------------
    # Initialization subfunctions
    # ----------------------------

    def _styled_label(self, text: str, style: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(style)
        return label

    def _init_value_line(self, name: str):
        line = QHBoxLayout()
        self.label_name = self._styled_label(f"{name}:", styleH2)
        self.lineedit_value = QLineEdit(str(self.value))
        self.lineedit_value.editingFinished.connect(self.input_changed)
        self.label_unit = self._styled_label(self.unit, styleH3)

        for widget in (self.label_name, self.lineedit_value, self.label_unit):
            line.addWidget(widget)
        line.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setLayout(line)
        self.layout.addWidget(container)

    def _init_slider_line(self):
        line = QHBoxLayout()
        self.label_min_value = self._styled_label(f"{self.min_value} {self.unit}", styleH3)
        self.label_max_value = self._styled_label(f"{self.max_value} {self.unit}", styleH3)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(int(self.min_value * self.ratio), int(self.max_value * self.ratio))
        self.slider.valueChanged.connect(self.slider_position_changed)

        for widget in (self.label_min_value, self.slider, self.label_max_value):
            line.addWidget(widget)
        line.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setLayout(line)
        self.layout.addWidget(container)

    # ----------------------------
    # Event handling
    # ----------------------------

    def slider_position_changed(self):
        self.value = self.slider.value() / self.ratio
        if self.integer:
            self.value = int(self.value)
        self.lineedit_value.setText(str(self.value))
        self.slider_changed.emit(self.value)

    def input_changed(self):
        """Triggered when user edits the numeric value."""
        try:
            val = float(self.lineedit_value.text())
        except ValueError:
            val = self.value  # revert to last valid value

        self.value = self._clamp(val, self.min_value, self.max_value)
        self.update_block()
        self.slider_changed.emit(self.value)

    # ----------------------------
    # Utilities
    # ----------------------------

    def update_block(self):
        """Sync text and slider position."""
        val = int(self.value) if self.integer else self.value
        self.lineedit_value.setText(str(val))
        self.slider.blockSignals(True)
        self.slider.setValue(int(val * self.ratio))
        self.slider.blockSignals(False)

    def get_value(self) -> float:
        return self.value

    def set_value(self, value: float):
        self.value = int(value) if self.integer else float(value)
        self.update_block()

    def set_min_max_slider_values(self, min_value: float, max_value: float, value: float | None = None):
        """Update slider bounds and optionally reset its current value."""
        self.min_value, self.max_value = min_value, max_value
        self.slider.setRange(int(min_value * self.ratio), int(max_value * self.ratio))
        if value is not None:
            self.set_value(value)
        self.label_min_value.setText(f"{min_value} {self.unit}")
        self.label_max_value.setText(f"{max_value} {self.unit}")

    def set_enabled(self, enabled: bool):
        """Enable or disable the whole block."""
        self.slider.setEnabled(enabled)
        self.lineedit_value.setEnabled(enabled)

    @staticmethod
    def _clamp(val, vmin, vmax):
        return max(vmin, min(vmax, val))



class SlicesOptionsWidget(QWidget):
    """
    Widget containing the smooth filters options.
    """

    options_changed = pyqtSignal(str)

    def __init__(self, parent):
        """
        Default Constructor.
        :param parent: Parent window of the main widget.
        """
        super().__init__(parent=None)
        self.layout = QVBoxLayout()
        self.parent = parent

        self.slider_horizontal = SliderBloc(name=translate('vertical_slice'), unit='',
                                      min_value=0, max_value=5, integer=True)
        self.slider_horizontal.set_value(1)
        self.slider_horizontal.slider_changed.connect(self.action_slider_changed)

        self.slider_vertical = SliderBloc(name=translate('horizontal_slice'), unit='',
                                      min_value=0, max_value=5, integer=True)
        self.slider_vertical.set_value(1)
        self.slider_vertical.slider_changed.connect(self.action_slider_changed)

        self.layout.addWidget(self.slider_horizontal)
        self.layout.addWidget(self.slider_vertical)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def set_sliders_range(self, height, width):
        """Update Sliders range. """
        self.slider_vertical.set_min_max_slider_values(1, height)
        self.slider_horizontal.set_min_max_slider_values(1, width)

    def action_slider_changed(self, event):
        """Action performed when a button is clicked."""
        sender = self.sender()
        self.options_changed.emit('tools_slice')

    def get_slices_values(self):
        """Returns pixels values for horizontal and vertical slices in the image."""
        vert = int(self.slider_vertical.get_value())
        hor = int(self.slider_horizontal.get_value())
        return hor, vert



class XYChartWidget(QWidget):
    """Widget to display 2D charts with multiple X-Y datasets."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = ''
        self.layout = QVBoxLayout(self)

        # Title label
        self.title_label = QLabel('', alignment=Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(
            "background-color: darkgray; font-weight:bold; color:white; font-size:20px;"
        )

        # Info label
        self.info_label = QLabel('', alignment=Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet(
            "background-color: lightgray; font-size:10px;"
        )

        # Chart area
        self.plot_chart_widget = PlotWidget()
        self.plot_chart_widget.showGrid(x=True, y=True)
        self.plot_chart = None

        # Default colors and pens
        self.pen = [
            mkPen(color=BLUE_IOGS, style=Qt.PenStyle.SolidLine, width=2.5),
            mkPen(color=ORANGE_IOGS, style=Qt.PenStyle.DashLine, width=2.5),
        ]
        self.brush = mkBrush(ORANGE_IOGS)

        # Data
        self.plot_x_data = []
        self.plot_y_data = []
        self.x_label = ''
        self.y_label = ''
        self.y_name = []
        self.legend_offset = (0, 0)

        # Layout
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.plot_chart_widget)
        self.layout.addWidget(self.info_label)

    # -------------------- API --------------------

    def set_data(self, x_axis, y_axis, x_label='', y_label=''):
        """
        Accepte :
        - x_axis : liste ou liste de listes
        - y_axis : liste ou liste de listes
        """
        # Force y_axis à être une liste de séries
        if not isinstance(y_axis[0], (list, np.ndarray)):
            y_axis = [y_axis]

        # Si x_axis est unique, on l'applique à toutes les séries Y
        if not isinstance(x_axis[0], (list, np.ndarray)):
            x_axis = [x_axis] * len(y_axis)

        # Conversion en numpy arrays
        self.plot_x_data = [np.array(x) for x in x_axis]
        self.plot_y_data = [np.array(y) for y in y_axis]

        self.x_label, self.y_label = x_label, y_label

    def set_legend(self, y_names, x_offset=0, y_offset=0):
        self.y_name = y_names if isinstance(y_names, (list, tuple)) else [y_names]
        self.legend_offset = (x_offset, y_offset)

    def refresh_chart(self, last=0):
        """Redraw the chart with the latest data."""
        self.plot_chart_widget.clear()

        # Legend
        legend = None
        if self.y_name:
            legend = self.plot_chart_widget.addLegend()
            if self.legend_offset != (0, 0):
                legend.setOffset(self.legend_offset)

        # Draw each curve
        for i, (x_data, y_data) in enumerate(zip(self.plot_x_data, self.plot_y_data)):
            if len(y_data) < 2:
                continue

            x_plot, y_plot = self._slice_data(x_data, y_data, last)
            name = self.y_name[i] if i < len(self.y_name) else None

            self.plot_chart_widget.plot(
                x_plot,
                y_plot,
                pen=self.pen[i % len(self.pen)],
                brush=self.brush,
                name=name,
            )

        # Axes & labels
        self._update_axes()

        # Legend style
        if legend:
            for _, label in legend.items:
                label.setText(f'<span style="color:black; font-size:12pt;">{label.text}</span>')

    def update_infos(self, show_stats=True):
        if show_stats and len(self.plot_y_data) == 1:
            y = self.plot_y_data[0]
            self.set_information(f'Mean = {np.mean(y):.2f} / Std = {np.std(y):.2f}')
        else:
            self.set_information('Data Acquisition In Progress')

    def set_title(self, title):
        self.title = title
        self.title_label.setText(title)

    def set_information(self, infos):
        self.info_label.setText(infos)

    def set_background(self, css_color):
        self.plot_chart_widget.setBackground(css_color)
        self.setStyleSheet(f"background:{css_color};")

    def clear_graph(self):
        self.plot_chart_widget.clear()

    def display_last(self, number=50):
        self.refresh_chart(last=number)

    # -------------------- Internes --------------------

    def _slice_data(self, x_data, y_data, last):
        """Return the last N points or all data if N=0."""
        if last <= 0 or len(x_data) <= last:
            return x_data, y_data
        return x_data[-last:], y_data[-last:]

    def _update_axes(self):
        """Update tick spacing, grid and axis labels."""
        if not self.plot_x_data or len(self.plot_x_data[0]) < 2:
            return
        x_axis = self.plot_chart_widget.getPlotItem().getAxis('bottom')
        x0 = self.plot_x_data[0]
        Te = x0[1] - x0[0]
        n = len(x0)
        x_axis.setTickSpacing(n / 20 * Te, n / 100 * Te)

        styles = {"color": "black", "font-size": "18px"}
        if self.x_label:
            self.plot_chart_widget.setLabel("bottom", self.x_label, **styles)
        if self.y_label:
            self.plot_chart_widget.setLabel("left", self.y_label, **styles)


class SliceXYWidget(XYChartWidget):
    """
    Widget containing a XY chart.
    """

    def __init__(self, parent=None):
        """
        Default Constructor.
        :param parent: Parent window of the main widget.
        """
        super().__init__(parent=parent)
        self.__show_grid = True

    def show_grid(self, value=True):
        """Change the grid display."""
        self.__show_grid = value

    def refresh_chart(self, last: int = 0):
        super().refresh_chart(last)
        self.plot_chart_widget.showGrid(x=self.__show_grid, y=self.__show_grid)