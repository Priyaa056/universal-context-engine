from mcp.registry import ToolRegistry
from mcp.mock_email_tool import MockEmailTool
from mcp.models import ToolType


def test_register_tool():
    registry = ToolRegistry()
    tool = MockEmailTool()

    registry.register(tool)

    assert registry.has_tool(ToolType.EMAIL)


def test_get_registered_tool():
    registry = ToolRegistry()
    tool = MockEmailTool()

    registry.register(tool)

    retrieved = registry.get_tool(ToolType.EMAIL)

    assert retrieved is tool


def test_list_tools():
    registry = ToolRegistry()

    registry.register(MockEmailTool())

    tools = registry.list_tools()

    assert len(tools) == 1
    assert tools[0].tool_type == ToolType.EMAIL


def test_unregistered_tool():
    import pytest

    registry = ToolRegistry()

    with pytest.raises(ValueError):
        registry.get_tool(ToolType.EMAIL)