from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class ToolType(Enum):
    EMAIL = "email"
    TASK = "task"
    WHATSAPP = "whatsapp"
    CALENDAR = "calendar"
    GITHUB = "github"
    CUSTOM_API = "custom_api"


class ToolStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    DRAFT_CREATED = "draft_created"


@dataclass(frozen=True)
class ToolInput:
    tool_type: ToolType
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ToolResult:
    tool_type: ToolType
    status: ToolStatus
    message: str
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ToolMetadata:
    name: str
    tool_type: ToolType
    description: str
    supported_intents: List[str] = field(default_factory=list)