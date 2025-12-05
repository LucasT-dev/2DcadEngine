import base64
import importlib
from uuid import UUID

from PyQt6.QtCore import Qt, QPointF, QIODevice, QBuffer
from PyQt6.QtGui import QPen, QBrush, QColor, QTransform, QFont, QPixmap
from PyQt6.QtWidgets import QGraphicsItem


def get_data(item: QGraphicsItem):
    return {
        "class": f"{type(item).__module__}.{type(item).__name__}",
        "z_value": item.zValue(),
        "visibility": item.isVisible(),
        "scale": item.scale(),
        "rotation": item.rotation(),
        "transform": transform_to_dict(item.transform()),
        "data": {
            str(k): safe_serialize(item.data(k))
            for k in range(0, 100)
            if item.data(k) is not None
        }
    }


def get_pen(item: QGraphicsItem):
    if hasattr(item, "pen"):
        pen = item.pen()
        return {
            "color": rgba_to_hex(pen.color()),
            "width": pen.width(),
            "style": penstyle_to_int(pen.style()),
        }
    return {}


def dict_to_pen(data: dict):
    pen = QPen()

    color: QColor = hex_to_rgba(data["color"])
    pen.setColor(color)
    pen.setWidth(data["width"])
    pen.setStyle(Qt.PenStyle(data["style"]))

    return pen


def get_brush(item: QGraphicsItem):
    if hasattr(item, "brush"):
        brush = item.brush()
        return {
            "color": rgba_to_hex(brush.color())
        }
    return {}


def dict_to_brush(data: dict) -> QBrush:
    brush = QBrush()
    brush.setColor(hex_to_rgba(data["color"]))
    return brush


def color_to_dict(color: QColor) -> dict:
    return {"r": color.red(), "g": color.green(), "b": color.blue(), "a": color.alpha()}


def color_from_dict(data: dict) -> QColor:
    return QColor(data["r"], data["g"], data["b"], data["a"])


def rgba_to_hex(color: QColor) -> str:
    """Convertit un dict RGBA en chaîne hexadécimale."""
    r, g, b, a = color.red(), color.green(), color.blue(), color.alpha()
    return "#{:02X}{:02X}{:02X}{:02X}".format(r, g, b, a)


def hex_to_rgba(hex_str: str) -> QColor:
    """Convertit une chaîne hexadécimale (#RRGGBBAA ou #RRGGBB) en QColor."""
    if not hex_str:
        return QColor(0, 0, 0, 255)

    hex_str = hex_str.strip().lstrip('#')

    # Si alpha manquant, on le considère comme FF (opaque)
    if len(hex_str) == 6:
        hex_str += "FF"

    if len(hex_str) != 8:
        raise ValueError(f"Format de couleur invalide : {hex_str}")

    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    a = int(hex_str[6:8], 16)

    return QColor(r, g, b, a)


def point_to_dict(point: QPointF) -> dict:
    return {"x": point.x(), "y": point.y()}


def point_from_dict(data: dict) -> QPointF:
    return QPointF(data["x"], data["y"])


def penstyle_to_int( style: Qt.PenStyle) -> int:
    return int(style.value)


def penstyle_from_int(value: int) -> Qt.PenStyle:
    return Qt.PenStyle(value)


def dict_to_transform(data: dict) -> QTransform:
    """
    Recrée un QTransform à partir d'une liste de 9 floats :
    [m11, m12, m13, m21, m22, m23, m31, m32, m33]
    """
    if data is None:
        return QTransform()  # Identité

    if not isinstance(data, (list, tuple)) or len(data) != 9:
        raise ValueError(f"Transform doit être une liste de 9 valeurs. Reçu : {data}")

    return QTransform(*data)


def transform_to_dict(transform: QTransform) -> list[float]:
    return [transform.m11(), transform.m12(), transform.m13(),
            transform.m21(), transform.m22(), transform.m23(),
            transform.m31(), transform.m32(), transform.m33(),
            ]


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
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    pixmap.save(buffer, fmt)  # JPG par défaut
    data = buffer.data()
    return base64.b64encode(data).decode("utf-8")


def pixmap_from_base64(data: str) -> QPixmap:
    pixmap = QPixmap()
    pixmap.loadFromData(base64.b64decode(data))
    return pixmap


def serialize_flags(item: QGraphicsItem) -> list[str]:
    flags = []
    all_flags = QGraphicsItem.GraphicsItemFlag

    for flag in all_flags:
        if item.flags() & flag:
            flags.append(flag.name)

    return flags


def deserialize_flags(flag_list: list[str]) -> QGraphicsItem.GraphicsItemFlag:
    flags = QGraphicsItem.GraphicsItemFlag(0)
    all_flags = QGraphicsItem.GraphicsItemFlag

    for flag in all_flags:
        if flag.name in flag_list:
            flags |= flag

    return flags

def resolve_class_from_path(dotted_path: str):
    """
    Convertit une chaîne 'module.submodule.ClassName' en la classe Python correspondante.
    Lève ImportError / AttributeError si ça échoue.
    """
    if not dotted_path or "." not in dotted_path:
        raise ValueError(f"Chemin de classe invalide : {dotted_path}")

    module_path, class_name = dotted_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    return cls