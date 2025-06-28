from PyQt6.QtWidgets import QGraphicsRectItem
from PyQt6.QtCore import QRectF, QPointF

from graphic_view_element.preview_manager.PreviewShape import PreviewShape


class SquareCenterPreview(PreviewShape):

    def create_preview_item(self, start: QPointF, end: QPointF):
        square = self._make_square_from_center(start, end)
        self.graphics_item = QGraphicsRectItem(square)
        self.graphics_item.setPen(self.pen)
        self.graphics_item.setBrush(self.brush)

    def update_item(self, start: QPointF, end: QPointF):
        square = self._make_square_from_center(start, end)
        self.graphics_item.setRect(square)

    def create_item(self, start: QPointF, end: QPointF):
        pass

    def _make_square_from_center(self, center: QPointF, edge: QPointF) -> QRectF:
        dx = edge.x() - center.x()
        dy = edge.y() - center.y()
        size = max(abs(dx), abs(dy))

        dx = size if dx >= 0 else -size
        dy = size if dy >= 0 else -size

        return QRectF(center.x() - dx, center.y() - dy, 2 * dx, 2 * dy).normalized()