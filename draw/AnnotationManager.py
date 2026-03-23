from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel


class AnnotationManager:
    def __init__(self, view):
        self.view = view
        self.viewport = view.viewport()
        self._labels = {}  # id -> (QLabel, (x, y))

    def add_label(self, id_: str, text: str, x: int, y: int, font: QFont=QFont("Arial", 8), style=None):
        if id_ in self._labels:
            raise ValueError(f"Label '{id_}' already exists.")

        label = QLabel(text, self.viewport)
        label.setFont(font)
        label.setStyleSheet(style or "color: white; background-color: rgba(0,0,0,0);")
        label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        label.adjustSize()
        label.move(x, y)
        label.show()

        self._labels[id_] = (label, (x, y))

    def update_text(self, id_: str, text: str):
        if id_ in self._labels:
            label, pos = self._labels[id_]
            label.setText(text)
            label.adjustSize()
            label.move(*pos)

    def move_label(self, id_: str, x: int, y: int):
        if id_ in self._labels:
            label, _ = self._labels[id_]
            label.move(x, y)
            self._labels[id_] = (label, (x, y))

    def remove_label(self, id_: str):
        if id_ in self._labels:
            label, _ = self._labels.pop(id_)
            label.setParent(None)
            label.deleteLater()

    def resize_all(self):
        """Repositionne tous les labels à leurs coordonnées absolues."""
        for id_, (label, pos) in self._labels.items():
            label.move(*pos)

