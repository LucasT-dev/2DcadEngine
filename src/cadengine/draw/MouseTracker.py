from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtGui import QMouseEvent, QWheelEvent
from PyQt6.QtWidgets import QGraphicsView, QGraphicsItem


class MouseTracker(QObject):
    mouseMoved = pyqtSignal(dict)
    mouseClicked = pyqtSignal(dict)
    mouseDoubleClicked = pyqtSignal(dict)
    mouseDragged = pyqtSignal(dict)
    mouseHovered = pyqtSignal(QGraphicsItem)
    mouseWheel = pyqtSignal(dict)

    def __init__(self, view: QGraphicsView):
        super().__init__()
        self.view = view

        self._scene_pos = None
        self._view_pos = None
        self._buttons = None
        self._hovered_item = None
        self._dragging = False

    def process_mouse_move(self, event: QMouseEvent):
        self._view_pos = event.pos()
        self._scene_pos = self.view.mapToScene(event.pos())
        self._buttons = event.buttons()

        item = self.view.itemAt(event.pos())

        # Valide seulement si toujours dans la scène
        if item != self._hovered_item:
            self._hovered_item = item

            # Vérifie que l'item est toujours valide avant d'émettre
            if item is not None and item.scene() == self.view.scene():
                self.mouseHovered.emit(item)

        self.mouseMoved.emit(self.get_mouse_state())

        if event.buttons():
            self.mouseDragged.emit(self.get_mouse_state())

    def process_mouse_press(self, event: QMouseEvent):
        self._buttons = event.buttons()
        self.mouseClicked.emit(self.get_mouse_state())

    def process_mouse_release(self, event: QMouseEvent):
        self._buttons = event.buttons()
        self._dragging = False

    def process_mouse_double_click(self, event: QMouseEvent):
        self._scene_pos = self.view.mapToScene(event.pos())
        self._buttons = event.buttons()
        self.mouseDoubleClicked.emit(self.get_mouse_state())

    def process_wheel(self, event: QWheelEvent):
        pos_scene = self.view.mapToScene(event.position().toPoint())
        self.mouseWheel.emit({
            "delta": event.angleDelta().y(),
            "scene_pos": pos_scene,
            "view_pos": event.position()
        })

    def get_mouse_state(self) -> dict:
        return {
            "scene_pos": self._scene_pos,
            "view_pos": self._view_pos,
            "buttons": self._buttons,
            "hovered_item": self._hovered_item
        }