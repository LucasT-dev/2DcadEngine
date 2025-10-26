from PyQt6.QtWidgets import QGraphicsLineItem
from PyQt6.QtCore import QPointF
from graphic_view_element._old.preview_manager.PreviewShape import PreviewShape


def snap_to_axis(p1: QPointF, p2: QPointF) -> QPointF:
    """
    Force la ligne à être horizontale ou verticale
    selon la direction dominante.
    """
    dx = p2.x() - p1.x()
    dy = p2.y() - p1.y()

    if abs(dx) > abs(dy):
        # Ligne horizontale
        return QPointF(p2.x(), p1.y())
    else:
        # Ligne verticale
        return QPointF(p1.x(), p2.y())

class RightLinePreview(PreviewShape):

    def create_preview_item(self, start: QPointF, end: QPointF):

        snapped_end = snap_to_axis(start, end)
        self.graphics_item = QGraphicsLineItem(start.x(), start.y(),
                                              snapped_end.x(), snapped_end.y())
        self.graphics_item.setPen(self.pen)

    def update_item(self, start: QPointF, end: QPointF):
        snapped_end = snap_to_axis(start, end)
        self.graphics_item.setLine(start.x(), start.y(),
                                   snapped_end.x(), snapped_end.y())