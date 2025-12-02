from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QWidget, QGraphicsView
from PyQt6.QtGui import QPainter, QColor, QPen, QFont


class HorizontalRuler(QWidget):
    def __init__(self, view: QGraphicsView, parent=None):

        super().__init__(parent)

        self.view = view

        # Configuration basique
        self._background_color = QColor("#2D2D2D")
        self._tick_color = QColor("#888888")
        self._text_color = QColor("#FFFFFF")
        self._font = QFont("Arial", 7)

        self.unit = "mm"  # 'px', 'mm', 'cm'
        self.dpi = self.logicalDpiX()  # ou self.view.logicalDpiX() pour précision

        self.setFixedHeight(20)

        self.spacing = 10
        self.major_tick = 10
        self.minor_tick = 2
        self.major_tick_interval = 50

    def update_style(self, background=None, tick=None, text=None, font_family=None, font_size=None):
        if background:
            self._background_color = QColor(background)
        if tick:
            self._tick_color = QColor(tick)
        if text:
            self._text_color = QColor(text)
        if font_family or font_size:
            current_size = self._font.pointSize() if font_size is None else font_size
            current_family = self._font.family() if font_family is None else font_family
            self._font = QFont(current_family, current_size)
        self.update()

    def set_parameter(self, height: int = 20,
                background_color: QColor = QColor("#2D2D2D"),
                tick_color: QColor = QColor("#888888"),
                text_color: QColor = QColor("#FFFFFF"),
                font = QFont("Arial", 7)
                ):
        self.setFixedHeight(height)
        self._background_color = background_color
        self._tick_color = tick_color
        self._text_color = text_color
        self._font = font
        self.update()

    def set_unit(self, unit: str):
        if unit not in ("px", "mm", "cm"):
            raise ValueError("Unit must be 'px', 'mm' or 'cm'")
        self.unit = unit
        self.update()

    def _convert_value(self, scene_value: float) -> float:
        """Convertit une coordonnée de scène (mm) dans l’unité choisie."""
        if self.unit == "px":
            # scène en mm → px à l'écran
            pixels_per_mm = self.view.logicalDpiX() / 25.4
            return scene_value * pixels_per_mm
        elif self.unit == "mm":
            return scene_value
        elif self.unit == "cm":
            return scene_value / 10.0
        return scene_value

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), self._background_color)
        painter.setFont(self._font)
        painter.setPen(QPen(self._tick_color))

        # Zone visible dans la scène (coordonnées réelles)
        scene_x_start = self.view.mapToScene(0, 0).x()
        scene_x_end = self.view.mapToScene(self.width(), 0).x()

        if scene_x_start > scene_x_end:
            scene_x_start, scene_x_end = scene_x_end, scene_x_start

        # Alignement des ticks sur la grille
        first_tick = int(scene_x_start // self.spacing) * self.spacing
        last_tick = int(scene_x_end)

        for x in range(first_tick, last_tick + self.spacing, self.spacing):
            x_view = self.view.mapFromScene(QPointF(x, 0)).x()
            if 0 <= x_view <= self.width():
                if x % self.major_tick_interval == 0:
                    painter.drawLine(int(x_view), 0, int(x_view), self.major_tick)
                    painter.setPen(QPen(self._text_color))

                    label = f"{self._convert_value(x):.1f}"
                    painter.drawText(int(x_view + 2), self.major_tick + 6, label)

                    painter.setPen(QPen(self._tick_color))
                else:
                    painter.drawLine(int(x_view), 0, int(x_view), self.minor_tick)

        painter.end()

class VerticalRuler(QWidget):

    def __init__(self, view: QGraphicsView, parent=None):

        super().__init__(parent)

        self.view = view
        self.setFixedWidth(20)

        # Configuration basique
        self._background_color = QColor("#2D2D2D")
        self._tick_color = QColor("#888888")
        self._text_color = QColor("#FFFFFF")
        self._font = QFont("Arial", 7)

        self.unit = "mm"  # 'px', 'mm', 'cm'
        self.dpi = self.logicalDpiX()  # ou self.view.logicalDpiX() pour précision

        self.spacing = 10
        self.major_tick = 10
        self.minor_tick = 2
        self.major_tick_interval = 50

    def update_style(self, background=None, tick=None, text=None, font_family=None, font_size=None):
        if background:
            self._background_color = QColor(background)
        if tick:
            self._tick_color = QColor(tick)
        if text:
            self._text_color = QColor(text)
        if font_family or font_size:
            current_size = self._font.pointSize() if font_size is None else font_size
            current_family = self._font.family() if font_family is None else font_family
            self._font = QFont(current_family, current_size)
        self.update()

    def set_parameter(self, height: int = 20,
                      background_color: QColor = QColor("#2D2D2D"),
                      tick_color: QColor = QColor("#888888"),
                      text_color: QColor = QColor("#FFFFFF"),
                      font=QFont("Arial", 7)
                      ):
        self.setFixedHeight(height)
        self._background_color = background_color
        self._tick_color = tick_color
        self._text_color = text_color
        self._font = font
        self.update()

    def set_unit(self, unit: str):

        if unit not in ("px", "mm", "cm"):
            raise ValueError("Unit must be 'px', 'mm' or 'cm'")
        self.unit = unit
        self.update()

    def _convert_value(self, scene_value: float) -> float:
        """Convertit une coordonnée de scène (mm) dans l’unité choisie."""
        if self.unit == "px":
            # scène en mm → px à l'écran
            pixels_per_mm = self.view.logicalDpiX() / 25.4
            return scene_value * pixels_per_mm
        elif self.unit == "mm":
            return scene_value
        elif self.unit == "cm":
            return scene_value / 10.0
        return scene_value

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), self._background_color)
        painter.setFont(self._font)
        painter.setPen(QPen(self._tick_color))

        # Zone visible dans la scène
        scene_y_start = self.view.mapToScene(0, 0).y()
        scene_y_end = self.view.mapToScene(0, self.height()).y()

        if scene_y_start > scene_y_end:
            scene_y_start, scene_y_end = scene_y_end, scene_y_start

        # Aligner la première graduation sur le multiple de spacing
        first_tick = int(scene_y_start // self.spacing) * self.spacing
        last_tick = int(scene_y_end)

        for y in range(first_tick, last_tick + self.spacing, self.spacing):
            y_view = self.view.mapFromScene(0, y).y()
            if 0 <= y_view <= self.height():
                if y % self.major_tick_interval == 0:
                    painter.drawLine(0, int(y_view), self.major_tick, int(y_view))
                    painter.setPen(QPen(self._text_color))

                    label = f"{self._convert_value(y):.1f}"
                    painter.drawText(self.major_tick - 8, int(y_view - 5), label)

                    painter.setPen(QPen(self._tick_color))
                else:
                    painter.drawLine(0, int(y_view), self.minor_tick, int(y_view))

        painter.end()


class CornerRuler(QWidget):

    def __init__(self, view: QGraphicsView):

        super().__init__()

        self.view = view

        self._background_color = QColor("#2D2D2D")

    def set_background_color(self, color: str):
        self._background_color = QColor(color)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        try:
            painter.fillRect(self.rect(), self._background_color)
        finally:
            painter.end()








