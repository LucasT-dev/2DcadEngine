import logging
from dataclasses import dataclass

from PyQt6.QtGui import QPainter, QColor

log = logging.getLogger(__name__)


@dataclass
class GraphicWindowConfig:
    """Valeurs par défaut de la vue 2D (modifiables à la création)."""
    scale: tuple = (1, -1)                       # repère inversé : Y vers le haut
    scene_rect: tuple = (-20, -20, 1500, 1500)   # x, y, largeur, hauteur
    unit: str = "mm"
    zoom: float = 1.0
    background_color: str = "#123456"
    render_hit = QPainter.RenderHint.Antialiasing
    pan_enable = True
    zoom_enable = True
    set_origin = "top-left"


class GraphicWindow:
    """Configurateur de MainCad : appelé via `configurator.init(maincad)`"""

    def __init__(self, config: GraphicWindowConfig | None = None, context=None):
        self.config = config or GraphicWindowConfig()
        self._context = context          # injectable pour les tests

    # ------------------------------------------------------------------ API
    def init(self, maincad):
        view = maincad.g_get_view
        cfg = self.config

        log.info("Load graphic interface")

        self._step("scale", view.g_set_scale, *cfg.scale)
        self._step("scene_rect", view.g_set_scene_rectangle, *cfg.scene_rect)
        self._step("background", view.g_set_background_color, cfg.background_color)
        self._step("unit", view.g_set_unit, cfg.unit)
        # Le zoom en dernier : il dépend de la taille de la scène et de la vue
        self._step("zoom", view.camera.zoom_to, cfg.zoom)
        self._step("render_hit", view.g_set_render_hit, cfg.render_hit)
        self._step("pan_enable", view.camera.set_pan_enabled, cfg.pan_enable)
        self._step("zoom_enable", view.camera.set_zoom_enabled, cfg.zoom_enable)
        self._step("set_origin", view.grid.set_origin_position, cfg.set_origin)

        view.grid.draw_line(color=QColor(0, 255, 0, 150), width=1,
                                       start_x=-10, start_y=0,
                                       end_x=view.width(), end_y=0)

        view.grid.draw_line(color=QColor(255, 0, 0, 150), width=1,
                                       start_x=0, start_y=view.height(),
                                       end_x=0, end_y=-10)

    @staticmethod
    def _step(name: str, func, *args):
        try:
            func(*args)
        except Exception:
            log.exception("Configuration de la vue : étape '%s' en échec", name)