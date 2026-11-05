from dataclasses import dataclass

from PyQt6.QtCore import QPointF

from graphic_view_element.GraphicItemManager.Handles.SnapIcon.SnapTypeEnum import SnapType


@dataclass
class PointOfInterest:
    point: QPointF
    snap_type: SnapType = SnapType.POINT_OF_INTEREST
    name: str | None = None        # identifiant
    is_default: bool = False       # True = généré automatiquement par la classe (recalculé à chaque resize)