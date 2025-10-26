from PyQt6.QtCore import QRectF, QPointF
from PyQt6.QtWidgets import QGraphicsEllipseItem

from graphic_view_element._old.preview_manager.PreviewShape import PreviewShape


class CircleCenterPreview(PreviewShape):

    def create_preview_item(self, start, end):

        rect = self._rect_from_center(start, end)
        self.graphics_item = QGraphicsEllipseItem(rect)
        self.graphics_item.setPen(self.pen)
        self.graphics_item.setBrush(self.brush)

    def update_item(self, start, end):
        rect = self._rect_from_center(start, end)
        self.graphics_item.setRect(rect)

    def create_item(self, start: QPointF, end: QPointF):
        pass

    def _rect_from_center(self, center, edge):
        dx = abs(edge.x() - center.x())
        dy = abs(edge.y() - center.y())
        r = max(dx, dy)  # pour faire un cercle, pas une ellipse
        return QRectF(center.x() - r, center.y() - r, 2 * r, 2 * r)