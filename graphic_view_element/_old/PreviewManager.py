from PyQt6.QtCore import QPointF

from draw.HistoryManager import AddItemCommand


class PreviewManager:

    def __init__(self, scene, style_element, element_registry):

        self.scene = scene
        self.style_element = style_element
        self.preview_shape = None
        self.start_pos = None

        self.element_registry = element_registry

        # outil (str ou Tool) -> classe de preview
        self.tool_map = {}

    def register_tool_preview(self, tool: str, preview_class):
        """Associer une preview à un nom d’outil (Tool ou str)."""
        self.tool_map[str(tool)] = preview_class

    def start_preview(self, pos: QPointF):
        self.clear_preview()
        self.start_pos = pos

        tool = self.style_element.get_tool()  # Peut être Tool.Line ou "circle_from_center"
        tool_key = str(tool)

        cls = self.tool_map.get(tool_key)

        if cls is None:
            return

        self.preview_shape = cls(self.style_element)
        self.preview_shape.create_preview_item(self.start_pos, self.start_pos)

        item = self.preview_shape.get_item()
        if item:
            item.setZValue(1000)
            self.scene.addItem(item)

    def create_custom_element(self, item):
        return self.scene.addItem(item)

    def create_item(self, pos: QPointF):

        # L'outil na pas de preview associé
        if not self.element_registry.contains_element(self.style_element.get_tool()):
            return

        element = self.element_registry.create_element(
            self.style_element.get_tool(),
            self.start_pos,
            pos,
            self.style_element
        )

        item = element.create_graphics_item()

        # historisation de la creation de l'item
        cmd = AddItemCommand(scene=self.scene, item=item, description=f"add item {item.__class__.__name__}")
        self.scene.undo_stack.push(cmd)

        self.scene.addItem(item)
        self.clear_preview()


    def update_preview(self, current_pos: QPointF):
        if self.preview_shape:
            self.preview_shape.update_item(self.start_pos, current_pos)

    def clear_preview(self):
        if self.preview_shape and self.preview_shape.get_item():
            self.scene.removeItem(self.preview_shape.get_item())
        self.preview_shape = None
        self.start_pos = None