import logging
from dataclasses import dataclass

# ------------------------------

log = logging.getLogger(__name__)


@dataclass
class GraphicWindowConfig:
    """Valeurs par défaut de la vue 2D (modifiables à la création)."""
    scale: tuple = (1, -1)                       # repère inversé : Y vers le haut
    scene_rect: tuple = (-20, -20, 1500, 1500)   # x, y, largeur, hauteur
    unit: str = "mm"
    zoom: float = 1.0
    background_color: str = "#ffffff"            # utilisé si le setting est absent
    background_setting_key: str = "graphic_window_background_color"


class GraphicWindow:
    """Configurateur de MainCad : appelé via `configurator.init(maincad)`.

    Chaque étape est isolée : si l'une échoue, les autres s'exécutent quand même
    et l'erreur est journalisée au lieu de faire planter l'onglet.
    """

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
        self._step("background", view.g_set_background_color, self._background_color())
        self._step("unit", view.g_set_unit, cfg.unit)
        # Le zoom en dernier : il dépend de la taille de la scène et de la vue
        self._step("zoom", view.camera.zoom_to, cfg.zoom)

    # -------------------------------------------------------------- helpers

    def _background_color(self):
        cfg = self.config

        return cfg.background_color


    @staticmethod
    def _step(name: str, func, *args):
        try:
            func(*args)
        except Exception:
            log.exception("Configuration de la vue : étape '%s' en échec", name)