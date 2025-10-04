from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsItem


class ItemInfoFormatter:

    def format_items(self, items: list[QGraphicsItem]) -> str:
        if not items:
            return "Aucun élément sélectionné."

        values = {
            "Type": {self._get_clean_type(item) for item in items},
            "Z-Value": {item.zValue() for item in items},
            "Position": {self._point(item.pos()) for item in items},
            "Bordder color": {self._color_rgb(item.pen().color()) for item in items if hasattr(item, "pen")},
            "Border Style": {item.pen().style().name for item in items if hasattr(item, "pen")},
            "Épaisseur": {item.pen().width() for item in items if hasattr(item, "pen")},
            "Fill color": {self._color_rgb(item.brush().color()) for item in items if hasattr(item, "brush")},
            "Width": self._dimensions(items, "width"),
            "Height": self._dimensions(items, "height"),
            "Rotation": self._rotation(items),
            "Scale": self._scale(items)
        }

        # Recupere les data de(s) l'item(s)
        data_fields = self._gather_item_data(items)

        # Format final
        lines = [f"<b> > Item information </b>", " ", f"<b>🧩 {len(items)} élément(s) sélectionné(s)</b><br><hr>"]

        for label, val_set in values.items():
            lines.append(self._format_line(label, val_set))

        if data_fields:
            lines.append("<hr><b>Données associées :</b>")
            for key, val_set in data_fields.items():
                lines.append(self._format_line(f"📎 {key}", val_set))

        return "<br>".join(lines)

    def _get_clean_type(self, item):
        cls = type(item).__name__
        # Tu peux filtrer ici si besoin
        return cls.replace("QGraphics", "").replace("Item", "")

    def _color_rgb(self, color: QColor):
        if not isinstance(color, QColor): return "Aucun"
        r, g, b = color.red(), color.green(), color.blue()
        return f"rgb({r}, {g}, {b})"

    def _point(self, point) -> str:
        if hasattr(point, "toPoint"):
            point = point.toPoint()
        return f"({point.x()}, {point.y()})"

    def _dimensions(self, items, dim_type: str) -> set:
        dims = set()
        for item in items:
            if hasattr(item, "rect"):
                rect = item.rect()
                val = getattr(rect, dim_type, lambda: None)()
                if val is not None:
                    dims.add(round(val, 2))
            elif hasattr(item, "line"):
                line = item.line()
                if dim_type == "width":
                    dims.add(abs(line.x2() - line.x1()))
                elif dim_type == "height":
                    dims.add(abs(line.y2() - line.y1()))
        return dims

    def _rotation(self, items) -> set:
        dims = set()
        for item in items:
                dims.add(abs(item.rotation()))
        return dims

    def _scale(self, items) -> set:
        dims = set()
        for item in items:
                dims.add(abs(item.scale()))
        return dims


    def _format_line(self, label: str, values: set) -> str:
        if not values:
            return f"<b>{label}:</b> <i>(non applicable)</i>"

        if len(values) == 1:
            val = next(iter(values))
            # Appliquer style si couleur
            if isinstance(val, str) and val.startswith("rgb("):
                return f"<b>{label}:</b> <span style='background-color:{val}; padding:2px 6px;'>{val}</span>"
            return f"<b>{label}:</b> {val}"
        else:
            return f"<b>{label}:</b> <i>Différents</i>"


    def _gather_item_data(self, items: list[QGraphicsItem]) -> dict:
        """Collecte toutes les données .data(i) présentes dans les items sélectionnés"""
        data_summary = {}

        # On teste les 0 à 50 premiers index — ajuste si tu en utilises plus
        for key in range(50):
            values = set()
            has_value = False

            for item in items:
                val = item.data(key)
                if val is not None:
                    values.add(str(val))
                    has_value = True

            if has_value:
                data_summary[f"data[{key}]"] = values

        return data_summary