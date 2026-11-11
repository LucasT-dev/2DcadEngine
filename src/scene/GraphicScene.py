from PyQt6.QtWidgets import QGraphicsScene


class GraphicScene(QGraphicsScene):
    def __init__(self, undo_stack, parent=None):
        super().__init__(parent)
        self.undo_stack = undo_stack

        self._plan_scene = None
        self._plan_visible = True
        self._plan_opacity = 1.0


    def set_background_plan(self, plan_scene: QGraphicsScene | None):

        if plan_scene is self._plan_scene:
            return
        if self._plan_scene is not None:
            self._plan_scene.changed.disconnect(self._on_plan_changed)

        self._plan_scene = plan_scene

        if plan_scene is not None:
            pass
            plan_scene.clearSelection()  # sinon les contours de sélection sont dessinés aussi
            plan_scene.changed.connect(self._on_plan_changed)

        self._invalidate_background()
        for v in self.views():
            v.resetCachedContent()
            v.viewport().update()
            v.viewport().repaint()

    def set_plan_visible(self, visible: bool):
        self._plan_visible = visible
        self._invalidate_background()

    def set_plan_opacity(self, opacity: float):
        self._plan_opacity = max(0.0, min(1.0, opacity))
        self._invalidate_background()

    # ---- interne ----
    def _invalidate_background(self):
        rect = self.sceneRect()
        if self._plan_scene is not None:
            rect = rect.united(self._plan_scene.sceneRect())
        self.invalidate(rect, QGraphicsScene.SceneLayer.BackgroundLayer)

    def _on_plan_changed(self, regions):
        # le plan a changé : on ne redessine que les zones modifiées
        for r in regions:
            self.invalidate(r, QGraphicsScene.SceneLayer.BackgroundLayer)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        if self._plan_scene is None or not self._plan_visible:
            return

        painter.save()
        try:
            painter.setOpacity(self._plan_opacity)
            self._plan_scene.render(painter, rect, rect, Qt.AspectRatioMode.IgnoreAspectRatio)
        except Exception:
            log.exception("Erreur de rendu du fond de plan")
        finally:
            painter.restore()