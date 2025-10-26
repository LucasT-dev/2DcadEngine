from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsRectItem

from graphic_view_element._old.preview_manager.PreviewShape import PreviewShape


class SquarePreview(PreviewShape):

    def create_preview_item(self, start: QPointF, end: QPointF):

        square = self._make_square_from_corner(start, end)
        self.graphics_item = QGraphicsRectItem(square)
        self.graphics_item.setPen(self.pen)
        self.graphics_item.setBrush(self.brush)

    def update_item(self, start: QPointF, end: QPointF):
        square = self._make_square_from_corner(start, end)
        self.graphics_item.setRect(square)

    def create_item(self, start: QPointF, end: QPointF):
        pass

    def _make_square_from_corner(self, start: QPointF, end: QPointF) -> QRectF:
        dx = end.x() - start.x()
        dy = end.y() - start.y()

        size = max(abs(dx), abs(dy))
        dx = size if dx >= 0 else -size
        dy = size if dy >= 0 else -size

        return QRectF(start, QPointF(start.x() + dx, start.y() + dy)).normalized()