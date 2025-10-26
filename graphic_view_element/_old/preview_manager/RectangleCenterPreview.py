from PyQt6.QtCore import QRectF, QPointF
from PyQt6.QtWidgets import QGraphicsRectItem

from graphic_view_element._old.preview_manager.PreviewShape import PreviewShape


class RectangleCenterPreview(PreviewShape):

    def create_preview_item(self, start: QPointF, end: QPointF):
        rect = self._make_rect_from_center(start, end)
        self.graphics_item = QGraphicsRectItem(rect)
        self.graphics_item.setPen(self.pen)
        self.graphics_item.setBrush(self.brush)

    def update_item(self, start: QPointF, end: QPointF):
        rect = self._make_rect_from_center(start, end)
        self.graphics_item.setRect(rect)

    def create_item(self, start: QPointF, end: QPointF):
        pass

    def _make_rect_from_center(self, center: QPointF, edge: QPointF) -> QRectF:
        dx = abs(edge.x() - center.x())
        dy = abs(edge.y() - center.y())
        return QRectF(center.x() - dx, center.y() - dy, 2 * dx, 2 * dy)