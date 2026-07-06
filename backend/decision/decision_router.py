from enum import Enum
from dataclasses import dataclass

from .models import DecisionResult, IntentType


class RouteType(Enum):
    ANSWER_PIPELINE = "answer_pipeline"
    TOOL_PIPELINE = "tool_pipeline"
    CLARIFICATION_PIPELINE = "clarification_pipeline"
    SEARCH_PIPELINE = "search_pipeline"


@dataclass(frozen=True)
class RouteResult:
    route: RouteType
    decision: DecisionResult
    reason: str


class DecisionRouter:
    """
    Routes a decision to the correct downstream pipeline.
    It does not execute tools or generate answers.
    """

    def route(self, decision: DecisionResult) -> RouteResult:
        if decision is None:
            raise ValueError("Decision cannot be None")

        if decision.intent == IntentType.CLARIFY:
            return RouteResult(
                route=RouteType.CLARIFICATION_PIPELINE,
                decision=decision,
                reason="Decision requires clarification.",
            )

        if decision.intent in [IntentType.SEND_EMAIL, IntentType.CREATE_TASK]:
            return RouteResult(
                route=RouteType.TOOL_PIPELINE,
                decision=decision,
                reason="Decision requires tool execution.",
            )

        if decision.intent == IntentType.SEARCH_KNOWLEDGE:
            return RouteResult(
                route=RouteType.SEARCH_PIPELINE,
                decision=decision,
                reason="Decision requires knowledge search.",
            )

        return RouteResult(
            route=RouteType.ANSWER_PIPELINE,
            decision=decision,
            reason="Decision can be handled by answer pipeline.",
        )