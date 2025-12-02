import uuid
from enum import Enum

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPen, QBrush, QFont


class ToolMode(Enum):
    CLICK_CLICK = 1
    CLICK_DRAG = 2


class StyleElement:

    def __init__(self):

        # Bordure
        self._border_color: QColor = QColor(255, 255, 255, 255)
        self._border_width: int = 2
        self._border_style: Qt.PenStyle = Qt.PenStyle.SolidLine

        # Remplissage
        self._fill_color: QColor = QColor(0, 0, 0, 0)  # transparent par défaut

        self._z_value = 0

        # Text
        self._text_color = QColor(0, 255, 0, 255)
        self._text: str = "Text"
        self._font = QFont("Arial", 14)
        self._text_width: int = 10

        # Data
        self._key: int = 0
        self._value = uuid.uuid4()

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


    def get_z_value(self) -> int:
        return self._z_value

    def set_z_value(self, z: int):
        self._z_value = z


    # Text
    def get_text_color(self) -> QColor:
        return self._text_color

    def set_text_color(self, color: QColor):
        self._text_color = color

    def get_text(self) -> str:
        return self._text

    def set_text(self, text: str):
        self._text = text

    def get_font(self) -> QFont:
        return self._font

    def set_font(self, font: QFont):
        self._font = font

    def get_text_width(self) -> int:
        return self._text_width

    def set_width(self, width: int):
        self._text_width = width

    # Data
    def get_key(self) -> int:
        return self._key

    def set_key(self, key: int):
        self._key = key


    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = value



    def get_tool(self) -> str:
        return self._tool

    def get_mode(self) -> ToolMode:
        return self._mode

    def set_tool(self, tool: str):
        self._tool = tool

    def set_mode(self, mode: ToolMode.CLICK_DRAG):
        self._mode = mode