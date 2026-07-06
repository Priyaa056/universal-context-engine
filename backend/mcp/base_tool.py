from abc import ABC, abstractmethod

from .models import ToolInput, ToolMetadata, ToolResult


class BaseTool(ABC):
    """Base interface for all MCP tools."""

    @property
    @abstractmethod
    def metadata(self) -> ToolMetadata:
        pass

    @abstractmethod
    def execute(self, tool_input: ToolInput) -> ToolResult:
        pass