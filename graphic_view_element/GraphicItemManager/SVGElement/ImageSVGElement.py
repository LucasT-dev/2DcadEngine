import os
import uuid
from pathlib import Path

from PyQt6.QtGui import QTransform
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsItem

from libs.cadengine.graphic_view_element.GraphicItemManager.Handles.HandleStyle import HandleStyle, DEFAULT_STYLE
from libs.cadengine.graphic_view_element.GraphicItemManager.SVGElement.ImageSVGResizable import ImageSVGResizable
from libs.cadengine.graphic_view_element.GraphicItemManager.GraphicElementObject import ElementObject


class ImageSVGElement(ElementObject):

    def create_graphics_item(self, first_point: QPointF, second_point: QPointF):

        current_dir = Path(__file__).parent
        image_path = str(current_dir.parents[2] / "image" / "image_icon.svg")

        if not os.path.exists(image_path):
            print("Image par défaut introuvable, utilisez un chemin valide.")
            return

        svg_item = ImageSVGResizable(image_path)

        svg_item.setZValue(self.get_style().get_z_value())

        rect = svg_item.boundingRect()

        # Point d’ancrage opposé

        target_rect = QRectF(first_point, second_point).normalized()

        native_rect = QRectF(rect).normalized()

        if native_rect.width() < 1e-6 or native_rect.height() < 1e-6:
            return
        if target_rect.width() < 1e-6 or target_rect.height() < 1e-6:
            return

        scale_x = target_rect.width() / native_rect.width()
        scale_y = target_rect.height() / native_rect.height()

        dx = target_rect.x() - native_rect.x() * scale_x
        dy = target_rect.y() + target_rect.height() + native_rect.y() * scale_y

        transform = QTransform(scale_x, 0, 0, -scale_y, dx, dy)

        svg_item.setTransform(transform)
        svg_item.setPos(0, 0)

        svg_item.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )

        svg_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        svg_item.setData(self.get_style().get_key(), self.get_style().get_value())
        svg_item.setAcceptHoverEvents(True)

        return svg_item

    @staticmethod
    def create_custom_graphics_item(first_point: QPointF, second_point: QPointF,
                                    image_source,
                                    z_value: int = 0,
                                    key: int = 0,
                                    value: str = uuid.uuid4(),
                                    transform: QTransform = QTransform(),
                                    visibility: bool = True,
                                    scale: float = 1.0,
                                    handle_style: HandleStyle = DEFAULT_STYLE,
                                    flags: QGraphicsItem.GraphicsItemFlag =
                                    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                                    QGraphicsItem.GraphicsItemFlag.ItemIsMovable):

        svg_item = ImageSVGResizable(image_source)

        target_rect = QRectF(first_point, second_point).normalized()

        svg_item.setTransform(transform)
        svg_item.setScale(scale)
        svg_item.setPos(target_rect.topLeft())

        svg_item.setZValue(z_value)

        svg_item.setFlags(flags)
        svg_item.setData(key, value)

        svg_item.set_handle_style(handle_style)

        return svg_item