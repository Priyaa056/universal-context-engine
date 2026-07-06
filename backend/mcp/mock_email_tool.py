from .base_tool import BaseTool
from .models import ToolInput, ToolMetadata, ToolResult, ToolStatus, ToolType


class MockEmailTool(BaseTool):
    """Creates a mock email draft without sending anything."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="Mock Email Tool",
            tool_type=ToolType.EMAIL,
            description="Creates an editable mock email draft.",
            supported_intents=["send_email"],
        )

    def execute(self, tool_input: ToolInput) -> ToolResult:
        payload = tool_input.payload

        recipient = payload.get("recipient", "")
        subject = payload.get("subject", "Generated Draft")
        body = payload.get("body", "")

        if not recipient:
            return ToolResult(
                tool_type=ToolType.EMAIL,
                status=ToolStatus.FAILED,
                message="Recipient is required to create email draft.",
                data={},
            )

        return ToolResult(
            tool_type=ToolType.EMAIL,
            status=ToolStatus.DRAFT_CREATED,
            message="Mock email draft created successfully.",
            data={
                "recipient": recipient,
                "subject": subject,
                "body": body,
                "editable": True,
            },
        )