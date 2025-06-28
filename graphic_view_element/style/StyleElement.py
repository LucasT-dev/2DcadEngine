from enum import Enum

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPen, QBrush

class ToolMode(Enum):
    CLICK_CLICK = 1
    CLICK_DRAG = 2


class StyleElement:

    def __init__(self):

        # Bordure
        self._border_color: QColor = QColor(0, 255, 0, 255)
        self._border_width: int = 2
        self._border_style: Qt.PenStyle = Qt.PenStyle.SolidLine

        # Remplissage
        self._fill_color: QColor = QColor(255, 0, 0, 255)  # transparent par défaut

        self._mode: ToolMode = ToolMode.CLICK_DRAG
        self._tool: str = "Mouse"


    def get_pen(self) -> QPen:
        color = self._border_color
        pen = QPen(color, self._border_width)
        pen.setStyle(self._border_style)
        return pen

    def get_brush(self) -> QBrush:
        color = self._fill_color
        return QBrush(color)


    def get_fill_color(self) -> QColor:
        return self._fill_color

    def set_fill_color(self, color: QColor):
        self._fill_color = color


    def get_border_color(self) -> QColor:
        return self._border_color

    def set_border_color(self, color: QColor):
        self._border_color = color


    def get_border_width(self) -> int:
        return self._border_width

    def set_border_width(self, width: int):
        self._border_width = width


    def get_border_style(self) -> Qt.PenStyle:
        return self._border_style

    def set_border_style(self, border_style: Qt.PenStyle):
        self._border_style = border_style



    def get_tool(self) -> str:
        return self._tool

    def get_mode(self) -> ToolMode:
        return self._mode

    def set_tool(self, tool: str):
        self._tool = tool

    def set_mode(self, mode: ToolMode.CLICK_DRAG):
        self._mode = mode