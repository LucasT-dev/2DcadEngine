from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor

from src.cadengine.graphic_view_element.GraphicItemManager.GraphicElementObject import GraphicElementObject


class GraphicElementManager:

    def __init__(self):

        self.item_register = {}


    def register_element(self, name: str, element: GraphicElementObject):

        self.item_register[name] = element

    def get_element(self, name: str) -> GraphicElementObject | None:
        if self.contains_element(name):
            return self.item_register.get(name)

        return None

    def create_element(self, name: str, start, end, style):
        if not self.contains_element(name):
            raise ValueError(f"Aucun élément enregistré sous le nom '{name}'")

        element = self.item_register.get(name)

        return element(start, end, style)

    def contains_element(self, name: str) -> bool:
        return self.item_register.__contains__(name)

    def get_all_items(self):
        """Retourne une liste de tous les items du registre."""
        return list(self.item_register.values())

    def add_shortcut(self, name: str, shortcut: Qt.Key):

        if self.contains_element(name):
            self.get_element(name).set_shortcut(shortcut)

    def add_cursor(self, name: str, cursor: Qt.CursorShape | QCursor):

        if self.contains_element(name):
            self.get_element(name).set_cursor(cursor)

    def has_preview(self, name: str) -> bool:
        if self.contains_element(name):
            if self.get_element(name).get_preview() is not None:
                return True
            return False
        return False

