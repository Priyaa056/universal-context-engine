from mcp.mock_email_tool import MockEmailTool
from mcp.models import ToolInput, ToolStatus, ToolType


def test_mock_email_tool_metadata():
    tool = MockEmailTool()

    metadata = tool.metadata

    assert metadata.tool_type == ToolType.EMAIL
    assert metadata.name == "Mock Email Tool"
    assert "send_email" in metadata.supported_intents


def test_mock_email_tool_creates_draft():
    tool = MockEmailTool()

    result = tool.execute(
        ToolInput(
            tool_type=ToolType.EMAIL,
            payload={
                "recipient": "manager@example.com",
                "subject": "Project Update",
                "body": "Here is the project summary.",
            },
        )
    )

    assert result.status == ToolStatus.DRAFT_CREATED
    assert result.data["editable"] is True
    assert result.data["recipient"] == "manager@example.com"


def test_mock_email_tool_requires_recipient():
    tool = MockEmailTool()

    result = tool.execute(
        ToolInput(
            tool_type=ToolType.EMAIL,
            payload={
                "subject": "Project Update",
                "body": "Here is the project summary.",
            },
        )
    )

    assert result.status == ToolStatus.FAILED