from typing import Dict, List

from .base_tool import BaseTool
from .models import ToolMetadata, ToolType


class ToolRegistry:
    """
    Stores and manages all available MCP tools.
    """

    def __init__(self):
        self._tools: Dict[ToolType, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Register a new tool."""
        self._tools[tool.metadata.tool_type] = tool

    def get_tool(self, tool_type: ToolType) -> BaseTool:
        """Retrieve a tool by its type."""
        if tool_type not in self._tools:
            raise ValueError(f"No tool registered for {tool_type.value}")

        return self._tools[tool_type]

    def has_tool(self, tool_type: ToolType) -> bool:
        """Check whether a tool is registered."""
        return tool_type in self._tools

    def list_tools(self) -> List[ToolMetadata]:
        """Return metadata for all registered tools."""
        return [tool.metadata for tool in self._tools.values()]