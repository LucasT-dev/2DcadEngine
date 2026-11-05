from PyQt6.QtCore import QRectF, QPointF
from PyQt6.QtWidgets import QGraphicsEllipseItem

from graphic_view_element.GraphicItemManager.GraphicElementObject import PreviewObject


class CirclePreview(PreviewObject):

    def create_preview_item(self, start, end):

        rect = self._make_square_from_corner(start, end)
        self._graphics_item = QGraphicsEllipseItem(rect)
        self._graphics_item.setPen(self.get_style().get_pen())
        self._graphics_item.setBrush(self.get_style().get_brush())

    def update_item(self, start, end):
        rect = self._make_square_from_corner(start, end)
        self._graphics_item.setRect(rect)

    def _make_square_from_corner(self, start: QPointF, end: QPointF) -> QRectF:
        dx = end.x() - start.x()
        dy = end.y() - start.y()

        size = max(abs(dx), abs(dy))
        dx = size if dx >= 0 else -size
        dy = size if dy >= 0 else -size

        return QRectF(start, QPointF(start.x() + dx, start.y() + dy)).normalized()