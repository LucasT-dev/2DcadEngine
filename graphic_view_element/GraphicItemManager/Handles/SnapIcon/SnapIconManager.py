from pathlib import Path

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer

from libs.cadengine.graphic_view_element.GraphicItemManager.Handles.SnapIcon.SnapTypeEnum import SnapType


class SnapIconManager:
    """
    Gère la configuration des icônes de snap.
    Permet à l'utilisateur de personnaliser ou désactiver une icône par SnapType.
    """

    DEFAULT_ICON_SIZE = 24

    def __init__(self, icon_size: int = DEFAULT_ICON_SIZE):
        self._icon_size = icon_size
        self._sources: dict[SnapType, str | QPixmap | None] = dict(self._default_sources())
        self._enabled: dict[SnapType, bool] = {t: True for t in SnapType}
        self._pixmap_cache: dict[SnapType, QPixmap] = {}

    # ---- valeurs par défaut ----

    @staticmethod
    def _default_icon_dir() -> Path:
        current_dir = Path(__file__).parent
        return current_dir.parents[3] / "image" / "snap_icon"

    @classmethod
    def _default_sources(cls) -> dict[SnapType, str]:
        icon_dir = cls._default_icon_dir()
        return {
            SnapType.ENDPOINT: str(icon_dir / "end_point_icon.svg"),
            SnapType.MIDPOINT: str(icon_dir / "middle_point_icon.svg"),
            SnapType.PROJECTION: str(icon_dir / "projection_point_icon.svg"),
            SnapType.INTERSECTION: str(icon_dir / "intersection_point_icon.svg"),
            SnapType.POINT_OF_INTEREST: str(icon_dir / "end_point_icon.svg"),
            SnapType.CENTRAL: str(icon_dir / "central_point_icon")
        }

    # methode publique

    def set_icon(self, snap_type: SnapType, source: str | Path | QPixmap):
        """
        Définit une icône personnalisée pour un type de snap.
        `source` : chemin vers un fichier (.svg, .png, QPixmap)
        """
        if isinstance(source, Path):
            source = str(source)
        self._sources[snap_type] = source
        self._pixmap_cache.pop(snap_type, None)  # invalide le cache pour ce type seulement

    def reset_icon(self, snap_type: SnapType):
        """Revient à l'icône par défaut pour ce type."""
        self._sources[snap_type] = self._default_sources().get(snap_type)
        self._pixmap_cache.pop(snap_type, None)

    def set_enabled(self, snap_type: SnapType, enabled: bool):
        """Active ou désactive l'affichage de l'icône pour ce type de snap."""
        self._enabled[snap_type] = enabled

    def is_enabled(self, snap_type: SnapType) -> bool:
        return self._enabled.get(snap_type, True)

    def set_icon_size(self, size: int):
        """Change la taille de rendu (px) des icônes SVG. Invalide tout le cache."""
        if size == self._icon_size:
            return
        self._icon_size = size
        self._pixmap_cache.clear()

    def get_pixmap(self, snap_type: SnapType) -> QPixmap | None:
        """
        Retourne le QPixmap à afficher pour ce type, ou None si désactivé / introuvable.
        """
        if not self.is_enabled(snap_type):
            return None

        if snap_type in self._pixmap_cache:
            return self._pixmap_cache[snap_type]

        source = self._sources.get(snap_type)
        if source is None:
            return None

        pixmap = self._load(source)
        if pixmap is None or pixmap.isNull():
            return None

        self._pixmap_cache[snap_type] = pixmap
        return pixmap

    # rendu interne

    def _load(self, source: str | QPixmap) -> QPixmap | None:
        if isinstance(source, QPixmap):
            return source  # fourni tel quel par l'utilisateur, pas de resize auto

        path = str(source)
        if path.lower().endswith(".svg"):
            return self._render_svg(path)

        pixmap = QPixmap(path)
        return pixmap if not pixmap.isNull() else None

    def _render_svg(self, path: str) -> QPixmap | None:

        renderer = QSvgRenderer(path)
        if not renderer.isValid():
            return None

        size = self._icon_size
        default_size = renderer.defaultSize()
        ratio = (default_size.width() / default_size.height()
                 if default_size.isValid() and default_size.height() > 0 else 1.0)

        w, h = (size, int(size / ratio)) if ratio >= 1 else (int(size * ratio), size)

        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        x, y = (size - w) / 2, (size - h) / 2
        renderer.render(painter, QRectF(x, y, w, h))
        painter.end()

        return pixmap