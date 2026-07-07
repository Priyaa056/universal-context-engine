from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict


class WorkflowStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    NEEDS_CLARIFICATION = "needs_clarification"


@dataclass(frozen=True)
class WorkflowRequest:
    question: str
    session_id: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class WorkflowResponse:
    status: WorkflowStatus
    answer: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)