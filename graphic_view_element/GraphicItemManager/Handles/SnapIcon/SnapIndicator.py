from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QGraphicsPixmapItem, QGraphicsItem

from libs.cadengine.graphic_view_element.GraphicItemManager.Handles.SnapIcon.SnapIconManager import SnapIconManager


class SnapIndicator(QGraphicsPixmapItem):

    _default_manager: SnapIconManager | None = None

    @classmethod
    def default_icon_manager(cls) -> SnapIconManager:
        """Manager partagé par défaut si aucun n'est fourni explicitement."""
        if cls._default_manager is None:
            cls._default_manager = SnapIconManager()
        return cls._default_manager

    def __init__(self, icon_manager: SnapIconManager | None = None):
        super().__init__()
        self.setZValue(10_000)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
        self._icon_manager = icon_manager or SnapIndicator.default_icon_manager()
        self.hide()

    def show_at(self, candidate: "SnapCandidate", scene):

        pixmap = self._icon_manager.get_pixmap(candidate.snap_type)

        if pixmap is None:
            self.hide()
            return

        self.setPixmap(pixmap)
        offset = QPointF(pixmap.width() / 2, pixmap.height() / 2)
        self.setPos(candidate.point - offset)

        if scene is None:
            return

        scene.addItem(self)

        self.show()

    def hide_indicator(self):

        self.hide()