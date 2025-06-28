from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor


class CursorManager:

    def __init__(self):
        self.tool_cursor_map = {}

    # Enregistrement
    def register_tool(self, tool_name: str, cursor: Qt.CursorShape | QCursor):
        self.tool_cursor_map[tool_name] = cursor

    # Accès
    def contains_tool(self, tool_name) -> bool:
        return self.tool_cursor_map.__contains__(tool_name)

    def get_cursor(self, tool_name) -> Qt.CursorShape | QCursor:
        return self.tool_cursor_map.get(tool_name)

    def get_registered_tools(self) -> list:
        return list(self.tool_cursor_map.keys())