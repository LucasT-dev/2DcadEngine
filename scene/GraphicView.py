import importlib
import logging

from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QPainter, QBrush, QColor, QFont, QCursor, QKeySequence, QAction, QPixmap, QPageSize, \
    QPageLayout, QTransform
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtWidgets import QGraphicsView, QWidget, QGridLayout, QGraphicsScene, QGraphicsItem, QGraphicsPixmapItem, \
    QGraphicsTextItem

from draw.CameraManager import Camera
from draw.CursorManager import CursorManager
from draw.AnnotationManager import AnnotationManager
from draw.GridManager import Grid
from draw.HistoryManager import RemoveItemCommand, ModifyItemPropertiesCommand, GroupItemsCommand, UngroupItemsCommand
from draw.MouseTracker import MouseTracker
from draw.RulesManager import HorizontalRuler, VerticalRuler, CornerRuler
from graphic_view_element.GraphicItemManager.GraphicElementManager import GraphicElementManager
from graphic_view_element.GraphicItemManager.GraphicElementObject import GraphicElementObject, ElementObject, \
    PreviewObject
from graphic_view_element.GraphicItemManager.Handles.ResizableGraphicsItem import ResizableGraphicsItem
from graphic_view_element.style.StyleElement import StyleElement


class GraphicViewContainer(QWidget):
    def __init__(self, scene: QGraphicsScene, show_ruler=False, ruler_positions=None, parent=None):
        super().__init__(parent)

        self.view = GraphicView(scene)
        self.show_ruler = show_ruler

        # Définir les positions par défaut si non spécifiées
        self.ruler_positions = ruler_positions or {
            "horizontal": "top",    # "top" ou "bottom"
            "vertical": "left"      # "left" ou "right"
        }

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.h_ruler = None
        self.v_ruler = None
        self.rule_corner = None

        self._setup_ui()

    def _setup_ui(self):
        if self.show_ruler:
            self.h_ruler = HorizontalRuler(self.view)
            self.v_ruler = VerticalRuler(self.view)
            self.rule_corner = CornerRuler(self.view)

            # Index du coin vide
            corner_row = 0 if self.ruler_positions["horizontal"] == "top" else 2
            corner_col = 0 if self.ruler_positions["vertical"] == "left" else 2

            # Position horizontale
            if self.ruler_positions["horizontal"] == "top":
                self.layout.addWidget(self.h_ruler, 0, 1)
            elif self.ruler_positions["horizontal"] == "bottom":
                self.layout.addWidget(self.h_ruler, 2, 1)

            # Position verticale
            if self.ruler_positions["vertical"] == "left":
                self.layout.addWidget(self.v_ruler, 1, 0)
            elif self.ruler_positions["vertical"] == "right":
                self.layout.addWidget(self.v_ruler, 1, 2)

            # Ajouter la vue graphique au centre
            self.layout.addWidget(self.view, 1, 1)

            # Ajouter le coin vide
            self.layout.addWidget(self.rule_corner, corner_row, corner_col)

            self.view.rulers = {"h": self.h_ruler, "v": self.v_ruler}

        else:
            self.layout.addWidget(self.view, 0, 0)

        self.layout.setColumnStretch(1, 1)
        self.layout.setRowStretch(1, 1)
        self.setLayout(self.layout)

    def set_ruler_position(self, horizontal: str = None, vertical: str = None):
        """Change dynamiquement la position des règles (top/bottom et left/right)."""
        if horizontal in ("top", "bottom"):
            self.ruler_positions["horizontal"] = horizontal

        if vertical in ("left", "right"):
            self.ruler_positions["vertical"] = vertical

        # Supprimer les anciens widgets de la grille
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget:
                self.layout.removeWidget(widget)
                widget.setParent(None)

        # Réinitialiser l'interface avec les nouvelles positions
        self._setup_ui()


class GraphicView(QGraphicsView):

    # Custom event signal
    tool_changed = pyqtSignal(str)
    selection_changed = pyqtSignal(list)

    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)

        # Composants métiers

        self.first_point = None
        self.grid = Grid(self)
        self.camera = Camera(self)
        self.cursor_manager = CursorManager()
        self.annotation_manager = AnnotationManager(self)

        # Event
        self.mouse_tracker = MouseTracker(self)


        # Element style
        self.style_element = StyleElement()

        # Element manager - Gestion des elements, preview, serialisation, resize
        self.element_manager = GraphicElementManager()

        self.scene().selectionChanged.connect(self.emit_selection_changed)

        # Configuration de base de la vue
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)


    def g_set_render_hit(self, render: QPainter.RenderHint):
        self.setRenderHint(render)

    def g_set_background_color(self, hex_color: str):
        self.setBackgroundBrush(QBrush(QColor(hex_color)))

    def g_set_scale(self, sx, sy):
        self.scale(sx, sy)

    def g_get_scale(self):
        transform = self.transform()
        print(f"M11 = {transform.m11()}")
        print(f"M22 = {transform.m22()}")
        return transform.m11(), transform.m22()

    def g_set_scene_rectangle(self, ax: float=-1000, ay: float=-1000, aw: float=2000, ah: float=2000):
        self.setSceneRect(ax, ay, aw, ah)

    def g_center_camera_on(self, pos_x: int, pos_y: int):
        self.centerOn(pos_x, pos_y)


    # --------------------start text annotation --------------------

    def g_add_text_annotation(self, id_: str, text: str, x: int, y: int, font: QFont, style):
        self.annotation_manager.add_label(id_, text, x, y, font=font, style=style)

    def g_update_text_annotation(self, id_: str, new_text: str):
        self.annotation_manager.update_text(id_, new_text)

    def g_remove_annotation(self, id_: str):
        self.annotation_manager.remove_label(id_)

    # -------------------- end text annotation ---------------------

    # -------------------- start scene unit ------------------------

    def g_set_unit(self, unit: str):
        if unit not in ("px", "mm", "cm"):
            raise ValueError("Unit must be 'px', 'mm' or 'cm'")

        if hasattr(self, 'rulers'):
            self.rulers["h"].unit = unit
            self.rulers["v"].unit = unit

            self._update_rulers()

    # -------------------- end scene unit --------------------------


    # -------------------- start style method ------------------

    def g_set_fill_color(self, color: QColor):
        self.style_element.set_fill_color(color)

    def g_set_border_color(self, color: QColor):
        self.style_element.set_border_color(color)

    def g_set_border_width(self, width: int):
        self.style_element.set_border_width(width)

    def g_set_border_style(self, border_style: Qt.PenStyle):
        self.style_element.set_border_style(border_style)

    def g_set_tool(self, tool: str):
        self.style_element.set_tool(tool)

        self.emit_tool_changed(tool)
        self._update_selection_mode(tool)

    def g_get_tool(self) -> str:
        return self.style_element.get_tool()

    # -------------------- end style method --------------------


    # -------------------- start item method --------------

    def g_get_items_selected(self) -> list[QGraphicsItem]:
        return self.scene().selectedItems()

    def g_get_items(self) -> list[QGraphicsItem]:
        return self.scene().items()

    def g_get_item_by_data(self, key: int, value) -> QGraphicsItem | None:
        """Recherche le premier item dont item.data(key) == value"""
        for item in self.scene().items():
            if item.data(key) == value:
                return item
        return None

    def g_get_items_by_data(self, key: int, value) -> list[QGraphicsItem]:
        return [item for item in self.scene().items() if item.data(key) == value]


    def g_change_fill_color_items_selected(self, fill_color: QColor):
        for item in self.scene().selectedItems():
            if hasattr(item, "setBrush"):
                old_item = item

                item.setBrush(QBrush(fill_color))

                cmd = ModifyItemPropertiesCommand(old_item, item, "change item style")
                self.scene().undo_stack.push(cmd)

    def g_change_border_color_items_selected(self, border_color: QColor):
        for item in self.scene().selectedItems():
            if hasattr(item, "setPen"):
                old_item = item
                pen = item.pen()
                pen.setColor(border_color)
                item.setPen(pen)

                cmd = ModifyItemPropertiesCommand(old_item, item, "change item style")
                self.scene().undo_stack.push(cmd)

    def g_change_border_width_items_selected(self, width: int):
        for item in self.scene().selectedItems():
            if hasattr(item, "setPen"):
                old_item = item
                pen = item.pen()
                pen.setWidth(width)
                item.setPen(pen)

                cmd = ModifyItemPropertiesCommand(old_item, item, "change item style")
                self.scene().undo_stack.push(cmd)

    def g_change_border_style_items_selected(self, style: Qt.PenStyle):
        for item in self.scene().selectedItems():
            if hasattr(item, "setPen"):
                old_item = item
                pen = item.pen()
                pen.setStyle(style)
                item.setPen(pen)

                cmd = ModifyItemPropertiesCommand(old_item, item, "change item style")
                self.scene().undo_stack.push(cmd)

    def g_change_z_value_items_selected(self, z_value: int | float):
        for item in self.scene().selectedItems():
            old_item = item
            item.setZValue(z_value)

            cmd = ModifyItemPropertiesCommand(old_item, item, "change item style")
            self.scene().undo_stack.push(cmd)

    def g_change_image_url_items_selected(self, url: str):
        for item in self.scene().selectedItems():
            if isinstance(item, QGraphicsPixmapItem):
                pixmap = QPixmap(url)
                if not pixmap.isNull():
                    old_item = item
                    item.setPixmap(pixmap)

                    cmd = ModifyItemPropertiesCommand(old_item, item, "change item style")
                    self.scene().undo_stack.push(cmd)
                else:
                    print(f"Failed to load image from URL: {url}")

    def g_up_z_value_items_selected(self):
        for item in self.scene().selectedItems():
            old_item = item
            item.setZValue(item.zValue() + 1)

            cmd = ModifyItemPropertiesCommand(old_item, item, "change item style")
            self.scene().undo_stack.push(cmd)

    def g_down_z_value_items_selected(self):
        for item in self.scene().selectedItems():
            old_item = item
            item.setZValue(item.zValue() - 1)

            cmd = ModifyItemPropertiesCommand(old_item, item, "change item style")
            self.scene().undo_stack.push(cmd)

    def g_send_items_selected_to_front(self):
        selected = self.scene().selectedItems()
        if not selected:
            return

        # Trouver les objets sélectionnables dans la scène
        selectable_items = [
            item for item in self.scene().items()
            if item.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        ]

        # Chercher le zValue max parmi les éléments sélectionnables
        max_z = max((item.zValue() for item in selectable_items), default=0)

        # Appliquer un zValue plus élevé à chaque sélectionné
        for i, item in enumerate(selected):
            old_item = item
            item.setZValue(max_z + i + 1)  # +i pour garder un ordre relatif

            cmd = ModifyItemPropertiesCommand(old_item, item, "change item style")
            self.scene().undo_stack.push(cmd)

    def g_send_items_selected_to_back(self):
        selected = self.scene().selectedItems()
        if not selected:
            return

        # Tous les éléments sélectionnables dans la scène
        selectable_items = [
            item for item in self.scene().items()
            if item.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        ]

        # Le plus petit z-value actuel
        min_z = min((item.zValue() for item in selectable_items), default=0)

        # Appliquer un z-value plus petit à chaque sélectionné
        for i, item in enumerate(selected):
            old_item = item
            item.setZValue(min_z - len(selected) + i - 1)

            cmd = ModifyItemPropertiesCommand(old_item, item, "change item style")
            self.scene().undo_stack.push(cmd)

    def g_group_selected_items(self):
        selected_items = self.scene().selectedItems()
        if not selected_items:
            return None

        cmd = GroupItemsCommand(self.scene, selected_items=selected_items)
        self.scene().undo_stack.push(cmd)
        return None

    def g_ungroup_items(self, items):

        selected_items = items
        if not selected_items:
            return None

        # On ne prend que le premier groupe sélectionné
        group = next((it for it in selected_items if isinstance(it, QGraphicsItem)), None)
        if not group:
            return None

        cmd = UngroupItemsCommand(self.scene, group)
        self.scene().undo_stack.push(cmd)

        return None

    def g_ungroup_selected_items(self):
        return self.g_ungroup_items(self.scene().selectedItems())

    def g_unselect_items(self) :
        self.scene().clearSelection()


    # -------------------- end item method ----------------


    # -------------------- start register object preview method-


    # Create custom item by user program

    def g_add_item(self, name: str, **kwargs):
        """Ajoute un élément personnalisé à la scène."""
        self.scene().addItem(self.element_manager.get_element(name).element.create_custom_graphics_item(**kwargs))

    def g_add_QGraphicitem(self, item: QGraphicsItem):
        self.scene().addItem(item)

    # delete selected item by user program
    def g_remove_selected_item(self):

        for item in self.scene().selectedItems():
            self.scene().removeItem(item)

    # delete item by user program
    def g_remove_item(self, item: QGraphicsItem):
        self.scene().removeItem(item)

    # -------------------- end register object preview method --


    # -------------------- start serialize/deserialize method---
    def g_serialize_item_scene(self) -> list[dict]:
        return self.g_serialize_items(self.scene().items())

    def g_serialize_items(self, item_list) -> list[dict]:
        """Parcourt tous les items de la scène et sérialise ceux appartenant à un GraphicElementObject."""
        if not self.scene():
            return []

        serialized_items = []

        # Récupère toutes les classes resizable enregistrées
        resizable_classes = [elem.resizable_class for elem in self.element_manager.get_all_items()]

        for item in item_list:

            parent = item.parentItem()
            if parent and any(isinstance(parent, cls) for cls in resizable_classes):
                continue  # ne pas enregistrer les enfants (déjà dans le groupe)

            # Vérifie si l'item est un Resizable (ou un type enregistré)
            if any(isinstance(item, cls) for cls in resizable_classes):

                # Vérifie que l'item possède bien une méthode to_dict
                if hasattr(item, "to_dict") and callable(item.to_dict):
                    serialized_items.append(item.to_dict())
                else:
                    print(f"[WARN] L'item {item} est resizable mais n'a pas de méthode to_dict()")

        return serialized_items

    def g_deserialize_items(self, data_list: list[dict]) -> list[QGraphicsItem]:
        """Reconstruit une liste d'items graphiques à partir d'une liste de dictionnaires JSON."""
        if not data_list:
            return []

        deserialized_items = []

        for entry in data_list:

            item_type = entry.get("type")

            if not item_type:
                print(f"[WARN] Entrée JSON sans type : {entry}")
                continue

            class_path = entry.get("data", {}).get("class")
            resizable_class = self.resolve_class_from_path(class_path)

            try:
                item = resizable_class.from_dict(data=entry)

                if item:
                    deserialized_items.append(item)
                else:
                    print(f"[WARN] from_dict() pour '{item_type}' a retourné None")
            except Exception as e:
                print(f"[ERROR] from_dict() failed for '{item_type}': {e}")

        return deserialized_items

    def resolve_class_from_path(self, dotted_path: str):
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

    def export_scene_to_pdf(self, scene: QGraphicsScene, filename: str, render_rect: QRectF,
                            format=QPageSize.PageSizeId.A4, orientation=QPageLayout.Orientation.Portrait):

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFileName(filename)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setPageSize(QPageSize(format))
        printer.setPageOrientation(orientation)

        page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
        painter = QPainter(printer)

        t = self.transform()
        flipped_x = t.m11() < 0
        flipped_y = t.m22() < 0

        # inversion locale pour le PDF
        fix = QTransform()
        fix.scale(-1 if flipped_x else 1, -1 if flipped_y else 1)

        fix.translate(
            -page_rect.width() if flipped_x else 0,
            -page_rect.height() if flipped_y else 0
        )

        painter.setWorldTransform(fix)

        scene.render(painter, target=page_rect, source=render_rect)
        painter.end()

    # -------------------- end serialize/deserialize method ----


    # -------------------- start register object view method ---

    def g_register_element(self, element_name: str, element_class: type[ElementObject],
                           preview_class: type[PreviewObject], resizable_class: ResizableGraphicsItem | None):
        """Associer une preview à un nom d’outil (Tool ou str)."""
        # Instancier preview_class avec self.style_element
        preview_instance = preview_class(style=self.style_element)
        element_instance = element_class(style=self.style_element)

        self.element_manager.register_element(name=element_name,
                                              element=GraphicElementObject(name=element_name,
                                                                            element_class=element_instance,
                                                                            preview_class=preview_instance,
                                                                            style=self.style_element)
                                              .set_resizable_class(resizable_class)

                                              )

    # -------------------- end register object view method -----


    # -------------------- start register shortcut tool --------

    def g_register_shortcut(self, name: str, key: Qt.Key):
        """Associe une touche Qt à un nom d’outil (ex: Qt.Key_L → 'line')"""
        self.element_manager.add_shortcut(name=name, shortcut=key)

    # -------------------- end register shortcut tool ----------


    # -------------------- start register cursor tool --------

    def g_register_cursor(self, name: str, cursor: Qt.CursorShape | QCursor):
        """Associe un cursor à un nom d’outil"""
        self.element_manager.add_cursor(name=name, cursor=cursor)

    def g_set_cursor(self, cursor: Qt.CursorShape | QCursor):
        self.setCursor(cursor)

    # -------------------- end register cursor tool ----------

    # -------------------- start history manager -------------

    def g_set_shortcut_undo_action(self):
        # Ctrl+Z
        undo_action = self.scene().undo_stack.createUndoAction(self, "undo")
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.addAction(undo_action)

    def g_set_shortcut_redo_action(self):
        # Ctrl+Y
        redo_action = self.scene().undo_stack.createRedoAction(self, "redo")
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.addAction(redo_action)

    def g_undo_action(self):
        undo_action = self.scene().undo_stack.createUndoAction(self, "undo")
        self.addAction(undo_action)

    def g_redo_action(self):
        undo_action = self.scene().undo_stack.createRedoAction(self, "redo")
        self.addAction(undo_action)

    def g_set_shortcut_delete_item(self):
        # --- Suppr pour supprimer ---
        delete_action = QAction("delete", self)
        delete_action.setShortcut(Qt.Key.Key_Delete)
        delete_action.triggered.connect(self.delete_selected_items)
        self.addAction(delete_action)

    def delete_selected_items(self):
        # Pour tous les items sélectionnés
        for item in list(self.g_get_items_selected()):
            cmd = RemoveItemCommand(self.scene, item)
            self.scene().undo_stack.push(cmd)

    def set_undo_limit(self, limit: int):

        self.scene().undo_stack.setUndoLimit(limit)

    # -------------------- end history manager ---------------


    # -------------------- private method --------------------

    def _update_rulers(self):
        """Mettre à jour les règles si elles existent"""
        if hasattr(self, 'rulers'):
            self.rulers["h"].update()
            self.rulers["v"].update()

    # -------------------- private method --------------------

    def g_get_mouse_state(self):
        return self.mouse_tracker.get_mouse_state()

    # Gestion d'affichage ou non de la zone de selection en fonction de l'outil
    def _update_selection_mode(self, tool: str):
        if tool == "mousse":
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        else:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)


    # -------------------- EVENT --------------------
    def wheelEvent(self, event):
        self.mouse_tracker.process_wheel(event)

        if not self.camera.handle_wheel(event):
            super().wheelEvent(event)

        # mise a jour des rulers
        self._update_rulers()


    def mousePressEvent(self, event):

        # Ignorer si clic molette
        if event.button() == Qt.MouseButton.MiddleButton:
            self.mouse_tracker.process_mouse_press(event)
            self.camera.handle_mouse_press(event)  # facultatif
            return

        self.mouse_tracker.process_mouse_press(event)

        if not self.camera.handle_mouse_press(event):
            super().mousePressEvent(event)

        # mise a jour des rulers
        self._update_rulers()

        # Création de la preview
        if self.element_manager.has_preview(self.g_get_tool()):
            self.first_point = self.mapToScene(event.pos())
            self.element_manager.get_element(self.g_get_tool()).get_preview().create_preview_item(self.mapToScene(event.pos()), self.mapToScene(event.pos()))
            self.scene().addItem(self.element_manager.get_element(self.g_get_tool()).get_preview().get_item())


    def mouseReleaseEvent(self, event):

        # Ignorer si clic molette
        if event.button() == Qt.MouseButton.MiddleButton:
            self.mouse_tracker.process_mouse_release(event)
            self.camera.handle_mouse_release(event)
            return

        self.mouse_tracker.process_mouse_release(event)

        if not self.camera.handle_mouse_release(event):
            super().mouseReleaseEvent(event)

        if self.element_manager.has_preview(self.g_get_tool()):
            self.g_remove_item(self.element_manager.get_element(self.g_get_tool()).get_preview().get_item())
            self.scene().addItem(self.element_manager.get_element(self.g_get_tool()).element.create_graphics_item(self.first_point, self.mapToScene(event.pos())))
            self.first_point = None

    def mouseDoubleClickEvent(self, event):
        self.mouse_tracker.process_mouse_double_click(event)
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event):
        self.mouse_tracker.process_mouse_move(event)

        if not self.camera.handle_mouse_move(event):
            super().mouseMoveEvent(event)

        if self.element_manager.has_preview(self.g_get_tool()) and self.first_point is not None:
            self.element_manager.get_element(self.g_get_tool()).get_preview().update_item(self.first_point, self.mapToScene(event.pos()))

    def resizeEvent(self, event):
        super().resizeEvent(event)

        self._update_rulers()

        self.annotation_manager.resize_all()

    def scrollContentsBy(self, dx: int, dy: int):
        super().scrollContentsBy(dx, dy)

        # mise a jour des rulers
        self._update_rulers()


    # @deprecated
    def keyPressEvent(self, event):

        if isinstance(self.scene().focusItem(), QGraphicsTextItem):
            super().keyPressEvent(event)
            return

        key = event.key()

        for item in self.element_manager.get_all_items():
            if item.shortcut == key:
                self.g_set_tool(item.name)

                if item.cursor is None:
                    self.unsetCursor()
                else:
                    self.g_set_cursor(item.cursor)

                event.accept()

        super().keyPressEvent(event)

    # -------------------- EVENT --------------------

    # -------------------- Start custom event -------

    def emit_tool_changed(self, tool_name: str):
        self.tool_changed.emit(tool_name)

    def emit_selection_changed(self):
        selected = self.scene().selectedItems()
        self.selection_changed.emit(selected)

    # -------------------- End custom event ---------

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())
        if painter.begin(self.viewport()):
            try:
                scale = self.transform().m11()
            finally:
                painter.end()
