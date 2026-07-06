from decision.decision_router import DecisionRouter
from mcp.executor import ToolExecutor
from mcp.mock_email_tool import MockEmailTool
from mcp.registry import ToolRegistry
from mcp.models import ToolInput, ToolStatus, ToolType


def test_router_executes_email_tool():
    registry = ToolRegistry()
    registry.register(MockEmailTool())

    executor = ToolExecutor(registry)

    router = DecisionRouter(executor)

    result = router.execute_tool(
        ToolInput(
            tool_type=ToolType.EMAIL,
            payload={
                "recipient": "manager@example.com",
                "subject": "Demo",
                "body": "Testing router integration.",
            },
        )
    )

    assert result.status == ToolStatus.DRAFT_CREATED
    assert result.data["recipient"] == "manager@example.com"