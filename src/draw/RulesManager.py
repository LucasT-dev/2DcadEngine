from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QWidget, QGraphicsView
from PyQt6.QtGui import QPainter, QColor, QPen, QFont

import math
from PyQt6.QtCore import Qt, QPoint, QPointF
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QWidget, QGraphicsView

from adapter.ScreenConverter import pixels_per_mm


class Ruler(QWidget):
    SUBDIVS = {1: 5, 2: 4, 5: 5}   # nb de sous-graduations par graduation majeure
    MIN_MAJOR_PX = 60              # espace mini entre deux graduations majeures

    def __init__(self, view: QGraphicsView,
                 orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(parent)
        self.view = view
        self.orientation = orientation
        self.unit = "mm"

        self._bg = QColor("#2D2D2D")
        self._tick = QColor("#888888")
        self._text = QColor("#FFFFFF")
        self._font = QFont("Arial", 7)
        self.major_len, self.minor_len = 10, 4

        if orientation == Qt.Orientation.Horizontal:
            self.setFixedHeight(20)
        else:
            self.setFixedWidth(20)

        # Redessiner quand la vue bouge ou zoome
        refresh = lambda *_: self.update()
        view.horizontalScrollBar().valueChanged.connect(refresh)
        view.verticalScrollBar().valueChanged.connect(refresh)
        view.horizontalScrollBar().rangeChanged.connect(refresh)
        view.verticalScrollBar().rangeChanged.connect(refresh)
        if hasattr(view, "zoom_changed"):
            view.zoom_changed.connect(refresh)

    def set_unit(self, unit: str):
        if unit not in ("px", "mm", "cm"):
            raise ValueError("Unit must be 'px', 'mm' or 'cm'")
        self.unit = unit
        self.update()

    def set_parameter(self,
                background_color: QColor = QColor("#2D2D2D"),
                tick_color: QColor = QColor("#888888"),
                text_color: QColor = QColor("#FFFFFF"),
                font = QFont("Arial", 7)
                ):

        self._bg = background_color
        self._tick = tick_color
        self._text = text_color
        self._font = font

    def _unit_factor(self) -> float:
        """Valeur affichée = mm de scène * facteur."""
        if self.unit == "mm":
            return 1.0
        if self.unit == "cm":
            return 0.1
        return pixels_per_mm(self.view)   # px à 100 %

    def _nice_major(self, px_per_unit: float):
        raw = self.MIN_MAJOR_PX / px_per_unit
        base = 10 ** math.floor(math.log10(raw))
        mant = next(m for m in (1, 2, 5, 10) if m * base >= raw)
        if mant == 10:
            mant, base = 1, base * 10
        return mant * base, self.SUBDIVS[mant]

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(event.rect(), self._bg)
        p.setFont(self._font)

        horiz = self.orientation == Qt.Orientation.Horizontal
        vp = self.view.viewport()
        t = self.view.transform()
        scale = abs(t.m11() if horiz else t.m22())   # pixels écran par mm de scène
        if scale == 0:
            return

        factor = self._unit_factor()
        major, subdiv = self._nice_major(scale / factor)
        minor = major / subdiv

        # décalage règle <-> viewport
        o = self.mapFromGlobal(vp.mapToGlobal(QPoint(0, 0)))
        offset = o.x() if horiz else o.y()

        # plage visible dans la scène
        a = self.view.mapToScene(0, 0)
        b = self.view.mapToScene(vp.width(), vp.height())
        s0, s1 = (a.x(), b.x()) if horiz else (a.y(), b.y())
        if s0 > s1:
            s0, s1 = s1, s0

        n0 = math.floor(s0 * factor / minor)
        n1 = math.ceil(s1 * factor / minor)

        for n in range(n0, n1 + 1):
            value = n * minor
            scene = value / factor
            pt = self.view.mapFromScene(
                QPointF(scene, 0) if horiz else QPointF(0, scene))
            pos = (pt.x() if horiz else pt.y()) + offset

            is_major = (n % subdiv == 0)
            length = self.major_len if is_major else self.minor_len
            p.setPen(QPen(self._tick))
            if horiz:
                p.drawLine(pos, 0, pos, length)
            else:
                p.drawLine(0, pos, length, pos)

            if is_major:
                p.setPen(QPen(self._text))
                label = f"{round(value, 6):g}"
                if horiz:
                    p.drawText(pos + 2, self.major_len + 8, label)
                else:
                    p.save()
                    p.translate(self.major_len + 8, pos - 2)
                    p.rotate(-90)
                    p.drawText(0, 0, label)
                    p.restore()
        p.end()
