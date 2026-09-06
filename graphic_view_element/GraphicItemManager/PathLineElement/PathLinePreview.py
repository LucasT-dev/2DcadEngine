from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QPainterPath
from PyQt6.QtWidgets import QGraphicsPathItem

from libs.cadengine.graphic_view_element.GraphicItemManager.GraphicElementObject import PreviewObject, \
    MultiPointPreviewObject


class PathLinePreview(MultiPointPreviewObject):

    def create_preview_item(self, start: QPointF, end: QPointF):
        self._points = [start]
        self._graphics_item = QGraphicsPathItem()
        self._graphics_item.setPen(self.get_style().get_pen())
        self._rebuild_path(end)

    def update_item(self, start: QPointF, end: QPointF):
        # 'start' n'est pas utilisé ici : le dernier sommet validé
        # est self._points[-1], le segment "volant" va jusqu'à 'end'.
        if self._graphics_item is None or not self._points:
            return
        self._rebuild_path(end)

    def _rebuild_path(self, live_point: QPointF):
        path = QPainterPath()
        path.moveTo(self._points[0])
        for point in self._points[1:]:
            path.lineTo(point)
        path.lineTo(live_point)

        self._graphics_item.setPath(path)
        self._graphics_item.show()
        self._graphics_item.update()