from .models import ToolInput, ToolResult
from .registry import ToolRegistry


class ToolExecutor:
    """
    Executes MCP tools using the Tool Registry.
    """

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def execute(self, tool_input: ToolInput) -> ToolResult:
        """
        Find the appropriate tool and execute it.
        """
        tool = self.registry.get_tool(tool_input.tool_type)

        return tool.execute(tool_input)