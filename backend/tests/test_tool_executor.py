from mcp.executor import ToolExecutor
from mcp.mock_email_tool import MockEmailTool
from mcp.models import ToolInput, ToolStatus, ToolType
from mcp.registry import ToolRegistry


def test_executor_runs_email_tool():
    registry = ToolRegistry()
    registry.register(MockEmailTool())

    executor = ToolExecutor(registry)

    result = executor.execute(
        ToolInput(
            tool_type=ToolType.EMAIL,
            payload={
                "recipient": "manager@example.com",
                "subject": "Project Update",
                "body": "Here is today's update.",
            },
        )
    )

    assert result.status == ToolStatus.DRAFT_CREATED
    assert result.data["recipient"] == "manager@example.com"


def test_executor_fails_for_unregistered_tool():
    import pytest

    registry = ToolRegistry()
    executor = ToolExecutor(registry)

    with pytest.raises(ValueError):
        executor.execute(
            ToolInput(
                tool_type=ToolType.EMAIL,
                payload={}
            )
        )