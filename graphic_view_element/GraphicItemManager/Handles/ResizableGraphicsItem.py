from abc import abstractmethod

from PyQt6.QtCore import QPointF

from graphic_view_element.GraphicItemManager.Handles.Handle import Handle




class ResizableGraphicsItem:

    def __init__(self):
        self.handles = {}  # Dictionnaire pour stocker les Handles
        self._old_geometry = None  # Pour gérer l'historique des modifications

    def add_handle(self, role: str, position: QPointF):
        """Ajoute un handle à l'item."""
        handle = Handle(self, position, role)
        self.handles[role] = handle

    def handle_moved(self, role: str, new_pos: QPointF):
        """À implémenter par les sous-classes."""
        raise NotImplementedError("Cette méthode doit être implémentée.")

    def update_handles_position(self):
        """À implémenter par les sous-classes."""
        raise NotImplementedError("Cette méthode doit être implémentée.")

    def handle_press(self, role: str, position: QPointF):
        """À implémenter par les sous-classes."""
        raise NotImplementedError("Cette méthode doit être implémentée.")

    def handle_released(self, role: str, position: QPointF):
        """À implémenter par les sous-classes."""
        raise NotImplementedError("Cette méthode doit être implémentée.")

    def select_handle(self, select: bool):
        for handle in self.handles.values():
            handle.setVisible(select)

    def save_item_geometry(self):
        """À implémenter par les sous-classes."""
        raise NotImplementedError("Cette méthode doit être implémentée.")

    def save_history_geometry(self):
        """À implémenter par les sous-classes."""
        raise NotImplementedError("Cette méthode doit être implémentée.")


    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict): # -> GraphicElementObject:
        pass
