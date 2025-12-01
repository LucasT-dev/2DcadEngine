import json
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtWidgets import QGraphicsItem

from graphic_view_element._old.serialisation.SerializableGraphicsItem import SerializableGraphicsItem


def color_to_dict(color: QColor) -> dict:
    return {"r": color.red(), "g": color.green(), "b": color.blue(), "a": color.alpha()}

def color_from_dict(data: dict) -> QColor:
    return QColor(data["r"], data["g"], data["b"], data["a"])


def point_to_dict(point: QPointF) -> dict:
    return {"x": point.x(), "y": point.y()}

def point_from_dict(data: dict) -> QPointF:
    return QPointF(data["x"], data["y"])


def penstyle_to_int(style: Qt.PenStyle) -> int:
    return int(style.value)

def penstyle_from_int(value: int) -> Qt.PenStyle:
    return Qt.PenStyle(value)


class SceneSerializer:

    @staticmethod
    def serialize_items(items):
        """Sérialise un ou plusieurs items en liste de dictionnaires"""
        if isinstance(items, QGraphicsItem):
            items = [items]  # enveloppe dans une liste

        serialized = []

        for item in items:

            # Retire les items enfant des groupe d'item
            if item.parentItem() is not None:
                continue

            try:
                if isinstance(item, SerializableGraphicsItem):
                    item_to_dict = item.to_dict()
                    serialized.append(item_to_dict)

            except Exception as e:
                print(f"[WARN] Impossible de sérialiser {item}: {e}")
                continue

        return serialized

    @staticmethod
    def deserialize_items(items_data):
        """Reconstruit une liste d'items depuis une liste de dictionnaires"""
        new_items = []
        for data in items_data:
            try:
                new_items.append(SerializableGraphicsItem.from_dict(data))
            except Exception as e:
                print(f"[WARN] Impossible de désérialiser {data}: {e}")
                continue
        return new_items

    @staticmethod
    def save_to_file(items, filename: str):
        """Sauvegarde tous les items sérialisables de la scène dans un fichier JSON"""

        serialized = SceneSerializer.serialize_items(items)

        print(f"serialisation : {serialized}")


        with open(filename, "w", encoding="utf-8") as f:
            json.dump(serialized, f, indent=2)

    @staticmethod
    def load_from_file(filename: str):
        """Recharge les items depuis un fichier JSON et les ajoute à la scène"""
        with open(filename, "r", encoding="utf-8") as f:
            items_data = json.load(f)

        return SceneSerializer.deserialize_items(items_data)

