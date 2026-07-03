from dataclasses import dataclass
from enum import Enum


class IntentType(Enum):
    ANSWER_ONLY = "answer_only"
    SUMMARIZE = "summarize"
    SEARCH_KNOWLEDGE = "search_knowledge"
    SEND_EMAIL = "send_email"
    CREATE_TASK = "create_task"
    CLARIFY = "clarify"


@dataclass(frozen=True)
class DecisionResult:
    intent: IntentType
    confidence: float
    action_required: bool
    reason: str


@dataclass(frozen=True)
class DecisionStatistics:
    total_decisions: int
    successful_decisions: int