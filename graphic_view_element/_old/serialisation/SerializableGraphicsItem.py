import base64
import importlib
from uuid import UUID

from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsItem, QGraphicsLineItem, QGraphicsPixmapItem, \
    QGraphicsTextItem, QGraphicsRectItem, QGraphicsItemGroup
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QPixmap, QTransform
from PyQt6.QtCore import QRectF, Qt, QBuffer, QIODevice, QPointF


def color_to_dict(color: QColor) -> dict:
    return {"r": color.red(), "g": color.green(), "b": color.blue(), "a": color.alpha()}

def color_from_dict(data: dict) -> QColor:
    return QColor(data["r"], data["g"], data["b"], data["a"])


def font_to_dict(font: QFont) -> dict:
    return {
        "family": font.family(),
        "pointSize": font.pointSize(),
        "bold": font.bold(),
        "italic": font.italic(),
        "underline": font.underline(),
    }

def font_from_dict(data: dict) -> QFont:
    f = QFont(data["family"], data["pointSize"])
    f.setBold(data["bold"])
    f.setItalic(data["italic"])
    f.setUnderline(data["underline"])
    return f


def pixmap_to_base64(pixmap: QPixmap, fmt: str = "JPG") -> str:
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)  # ✅ c’est ici qu’on met le mode
    pixmap.save(buffer, fmt)  # PNG par défaut, mais JPG ou autre possible
    data = buffer.data()
    return base64.b64encode(data).decode("utf-8")


def pixmap_from_base64(data: str) -> QPixmap:
    pixmap = QPixmap()
    pixmap.loadFromData(base64.b64decode(data))
    return pixmap


def penstyle_to_int(style: Qt.PenStyle) -> int:
    return int(style.value)

def penstyle_from_int(value: int) -> Qt.PenStyle:
    return Qt.PenStyle(value)


def dict_to_transform(data: dict) -> QTransform:
    transform = QTransform()
    transform.setMatrix(
        data["m11"], data["m12"], data["m13"],
        data["m21"], data["m22"], data["m23"],
        data["m31"], data["m32"], data["m33"]
    )
    return transform

def transform_to_dict(transform: QTransform) -> dict:
    return {
        "m11": transform.m11(),
        "m12": transform.m12(),
        "m13": transform.m13(),
        "m21": transform.m21(),
        "m22": transform.m22(),
        "m23": transform.m23(),
        "m31": transform.m31(),
        "m32": transform.m32(),
        "m33": transform.m33(),
    }


def safe_serialize(value):
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, UUID):
        return str(value)  # UUID → str
    if isinstance(value, QColor):
        return value.red(), value.green(), value.blue(), value.alpha()
    return str(value)  # fallback générique

def safe_deserialize(key, value):
    if key == "uuid":
        return UUID(value)
    return value


class SerializableGraphicsItem(QGraphicsItem):
    """Parent qui ajoute la sérialisation JSON aux QGraphicsItem dérivés."""

    def to_dict(self) -> dict:
        data = {
            "class": f"{type(self).__module__}.{type(self).__name__}",
            "z_value": self.zValue(),
            "visibility": self.isVisible(),
            "scale": self.scale(),
            "rotation": self.rotation(),
            "transform": transform_to_dict(self.transform()),
            "data": {
                str(k): safe_serialize(self.data(k))
                for k in range(0, 100)
                if self.data(k) is not None
            }
        }

        # si l'item a un rect (Ellipse, Rect…)
        if hasattr(self, "rect"):
            r: QRectF = self.rect()
            data["rect"] = {
                "x": r.x(),
                "y": r.y(),
                "w": r.width(),
                "h": r.height()
            }

        # Line
        if isinstance(self, QGraphicsLineItem):
            line = self.line()
            data["line"] = {
                "x1": line.x1(),
                "y1": line.y1(),
                "x2": line.x2(),
                "y2": line.y2(),
            }

        # si l'item a un pen/brush
        if hasattr(self, "pen"):
            pen = self.pen()
            data["pen"] = {
                "color": color_to_dict(pen.color()),
                "width": pen.width(),
                "style": penstyle_to_int(pen.style()),
            }

        # si l'item a un pen/brush
        if hasattr(self, "brush"):
            brush = self.brush()
            data["brush"] = {"color": color_to_dict(brush.color())}

        # Text
        if isinstance(self, QGraphicsTextItem):
            data["text"] = self.toPlainText()
            data["font"] = font_to_dict(self.font())
            data["default_text_color"] = color_to_dict(self.defaultTextColor())

            # Position absolue dans la scène
            data["pos"] = {"x": self.pos().x(), "y": self.pos().y()}


        # Pixmap
        if isinstance(self, QGraphicsPixmapItem):
            data["pixmap"] = pixmap_to_base64(self.pixmap())
            # Sauvegarde la géométrie
            data["pos"] = {"x": self.pos().x(), "y": self.pos().y()}
            data["offset"] = {"x": self.offset().x(), "y": self.offset().y()}

            # Si c’est un groupe, sérialiser ses enfants
        if hasattr(self, "childItems"):
            children = []
            for child in self.childItems():
                if isinstance(child, SerializableGraphicsItem):
                    children.append(child.to_dict())
            if children:
                data["children"] = children

        return data

    @classmethod
    def from_dict(self, data: dict):
        module_name, class_name = data["class"].rsplit(".", 1)
        module = importlib.import_module(module_name)
        klass = getattr(module, class_name)

        # Ellipse / Rect
        if issubclass(klass, (QGraphicsEllipseItem, QGraphicsRectItem)):
            rect_data = data["rect"]
            item = klass(QRectF(
                rect_data["x"], rect_data["y"],
                rect_data["w"], rect_data["h"]
            ))

        # Line
        elif issubclass(klass, QGraphicsLineItem):
            line_data = data["line"]
            item = klass(line_data["x1"], line_data["y1"], line_data["x2"], line_data["y2"])

        # Text
        elif issubclass(klass, QGraphicsTextItem):
            item = klass(data["text"])
            if "font" in data:
                item.setFont(font_from_dict(data["font"]))
            if "default_text_color" in data:
                item.setDefaultTextColor(color_from_dict(data["default_text_color"]))
            if "pos" in data:
                p = data["pos"]
                item.setPos(QPointF(p["x"], p["y"]))

        # Pixmap
        elif issubclass(klass, QGraphicsPixmapItem):
            print("pixmap")
            pixmap = pixmap_from_base64(data["pixmap"])

            item = klass(pixmap)
            # Restaure la géométrie si dispo
            if "pos" in data:
                item.setPos(QPointF(data["pos"]["x"], data["pos"]["y"]))
            if "offset" in data:
                item.setOffset(data["offset"]["x"], data["offset"]["y"])

        elif issubclass(klass, QGraphicsItemGroup):

            items = []
            # Recharger ses enfants
            for child_data in data.get("children", []):
                print(child_data)
                child = self.from_dict(child_data)
                if child is not None:
                    items.append(child)

            item = klass(items)

        else:
            item = klass()

        # Pen / Brush
        if "pen" in data and hasattr(item, "setPen"):
            pen_data = data["pen"]
            pen = QPen(color_from_dict(pen_data["color"]))
            pen.setWidth(pen_data["width"])
            pen.setStyle(Qt.PenStyle(pen_data["style"]))
            item.setPen(pen)

        if "brush" in data and hasattr(item, "setBrush"):
            brush_data = data["brush"]
            brush = QBrush(color_from_dict(brush_data["color"]))
            item.setBrush(brush)

        item.setZValue(data.get("z_value", 0))
        item.setVisible(data.get("visibility", True))
        item.setScale(data.get("scale", 1.0))
        item.setRotation(data.get("rotation", 0.0))
        item.setTransform(dict_to_transform(data.get("transform", QTransform().scale(1, -1))))

        for k, v in data.get("data", {}).items():
            item.setData(int(k), v)

        return item