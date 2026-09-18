from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor

from libs.cadengine.exception.GraphicElementExceptions import ElementAlreadyRegisteredError, ElementNotRegisteredError, \
    ElementCreationError
from libs.cadengine.graphic_view_element.GraphicItemManager.GraphicElementObject import GraphicElementObject


class GraphicElementManager:

    def __init__(self):
        self.item_register = {}

    def register_element(self, name: str, element: GraphicElementObject):
        """
        Enregistre un élément sous un nom.
        Lève ElementAlreadyRegisteredError si le nom existe déjà,
        sauf si overwrite=True est explicitement passé.
        """
        if self.contains_element(name):
            raise ElementAlreadyRegisteredError(name)

        self.item_register[name] = element

    def get_element(self, name: str) -> GraphicElementObject:
        """
        Retourne l'élément enregistré sous 'name'.
        Lève ElementNotRegisteredError si le nom n'existe pas.
        """
        if not self.contains_element(name):
            raise ElementNotRegisteredError(name, known_names=list(self.item_register.keys()))

        return self.item_register.get(name)

    def create_element(self, name: str, start, end, style):
        """
        Instancie un élément enregistré.
        Lève ElementNotRegisteredError si 'name' est inconnu,
        ElementCreationError si l'instanciation échoue.
        """
        element = self.get_element(name)  # lève déjà ElementNotRegisteredError si absent

        try:
            return element(start, end, style)
        except Exception as e:
            raise ElementCreationError(name, e) from e

    def contains_element(self, name: str) -> bool:
        return name in self.item_register

    def get_all_elements(self):
        """Retourne une liste de tous les items du registre."""
        return list(self.item_register.values())

    def add_shortcut(self, name: str, shortcut: Qt.Key):
        """Associe un raccourci clavier à un élément enregistré. Lève ElementNotRegisteredError si absent."""
        self.get_element(name).set_shortcut(shortcut)

    def add_cursor(self, name: str, cursor: Qt.CursorShape | QCursor):
        """Associe un curseur à un élément enregistré. Lève ElementNotRegisteredError si absent."""
        self.get_element(name).set_cursor(cursor)

    def has_preview(self, name: str) -> bool:
        """
        Indique si l'élément possède une preview.
        Ne lève pas d'exception : un nom inconnu renvoie simplement False,
        car cette méthode sert typiquement à des tests conditionnels
        (ex: dans le contrôleur, avant de savoir si l'outil est valide).
        """
        if not self.contains_element(name):
            return False
        return self.get_element(name).get_preview() is not None