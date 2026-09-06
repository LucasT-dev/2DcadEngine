from dataclasses import dataclass, field
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor



@dataclass
class HandleStyle:
    """Définit l'apparence d'un Handle. Librement personnalisable ou remplaçable."""

    shape: str = "ellipse"              # "ellipse" ou "rect"
    base_size: float = 8.0              # taille de base en pixels écran (avant zoom)
    min_size: float = 3.0               # taille minimum en pixels scène (zoom élevé)
    border_color: QColor = field(default_factory=lambda: QColor(0, 204, 204, 255))
    fill_color: QColor = field(default_factory=lambda: QColor(0, 0, 0, 0))
    border_width: float = 3.0
    cursor: Qt.CursorShape = Qt.CursorShape.SizeAllCursor
    z_value: float = 1000.0


# Quelques styles prêts à l'emploi, réutilisables tels quels ou comme base à dupliquer.
DEFAULT_STYLE = HandleStyle()


ANCHOR_STYLE = HandleStyle(
    shape="rect",
    base_size=9.0,
    border_color=QColor(0, 204, 204, 255),
    fill_color=QColor(0, 0, 0, 0), # r, g, b, a
)

CONTROL_STYLE = HandleStyle(
    shape="ellipse",
    base_size=6.0,
    border_color=QColor(255, 140, 0, 255),
    fill_color=QColor(0, 0, 0, 0),
    z_value=999.0,  # légèrement sous les ancrages si superposition
)

GUIDE_LINE_STYLE = HandleStyle(
    border_color=QColor(255, 140, 0, 150),  # même teinte que CONTROL_STYLE, plus transparente
    border_width=1.5,
)