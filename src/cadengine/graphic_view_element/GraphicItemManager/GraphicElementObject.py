from abc import abstractmethod

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QGraphicsItem

from src.cadengine.graphic_view_element.GraphicItemManager.Handles.ResizableGraphicsItem import ResizableGraphicsItem
from src.cadengine.graphic_view_element.style.StyleElement import StyleElement


class ElementObject:

    def __init__(self, style: StyleElement):
        self._style = style

    def get_style(self):
        return self._style

    @abstractmethod
    def create_graphics_item(self, **kwargs) -> QGraphicsItem:
        pass

    @abstractmethod
    def create_custom_graphics_item(self, **kwargs) -> QGraphicsItem:
        """Méthode à implémenter pour chaque type d'élément avec ses paramètres spécifiques."""
        pass

class PreviewObject:

    def __init__(self, style: StyleElement):

        self._graphics_item = None
        self._style = style


    def get_style(self):
        return self._style

    @abstractmethod
    def create_preview_item(self, start: QPointF, end: QPointF):
        pass

    @abstractmethod
    def update_item(self, start: QPointF, end: QPointF):
        pass

    def get_item(self):
        return self._graphics_item


class GraphicElementObject:

    def __init__(self, name: str, element_class: ElementObject, preview_class: PreviewObject, style: StyleElement):

        self.name = name # Nom de l'item

        self._cursor: Qt.CursorShape | QCursor = Qt.CursorShape.CrossCursor
        self._shortcut: Qt.Key = Qt.Key.Key_Escape

        self._style = style

        self._element: ElementObject             = element_class       # Class de création de l'item
        self._preview: PreviewObject             = preview_class       # Class de preview de l'item pour preview lors du dessin

        self._resizable_class: ResizableGraphicsItem | None = None

    def name(self):
        return self.name

    @property
    def element(self):
        return self._element



    def get_preview(self) -> PreviewObject:
        return self._preview

    @property
    def style_element(self):
        return self._style

    @property
    def cursor(self) -> Qt.CursorShape | QCursor:
        return self._cursor

    @property
    def shortcut(self) -> Qt.Key:
        return self._shortcut


    def set_resizable_class(self, cls: ResizableGraphicsItem):
        """Définit la classe de l'item graphique"""
        self._resizable_class = cls
        return self

    @property
    def resizable_class(self) -> type | None:
        return self._resizable_class


    def set_cursor(self, cursor: Qt.CursorShape | QCursor):
        self._cursor = cursor
        return self


    def set_shortcut(self, shortcut: Qt.Key):
        self._shortcut = shortcut
        return self
