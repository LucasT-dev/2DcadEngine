from dataclasses import dataclass
from enum import Enum, auto

from PyQt6.QtCore import QPointF


class SnapType(Enum):
    ENDPOINT = auto()           # extrémité (point d'ancrage d'un path, bout d'une ligne...)
    MIDPOINT = auto()           # milieu de segment
    CENTRAL = auto()            # Point central (cercle, rectangle)
    PROJECTION = auto()         # point projeté sur un segment (pas un point "nommé")
    INTERSECTION = auto()       # intersection entre deux lignes
    POINT_OF_INTEREST = auto()  # point générique fourni par un item, type non précisé


@dataclass
class SnapCandidate:
    point: QPointF
    snap_type: SnapType