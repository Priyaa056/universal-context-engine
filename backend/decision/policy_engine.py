from .models import DecisionResult, IntentType


class DecisionPolicyEngine:
    """
    Applies policy checks after intent classification.
    It decides whether the system can proceed or should ask clarification.
    """

    def apply(self, decision: DecisionResult, question: str) -> DecisionResult:
        if decision is None:
            return DecisionResult(
                intent=IntentType.CLARIFY,
                confidence=1.0,
                action_required=False,
                reason="No decision was provided.",
            )

        if question is None or not question.strip():
            return DecisionResult(
                intent=IntentType.CLARIFY,
                confidence=1.0,
                action_required=False,
                reason="Question is empty. Clarification required.",
            )

        if decision.intent == IntentType.SEND_EMAIL:
            if not self._has_recipient(question):
                return DecisionResult(
                    intent=IntentType.CLARIFY,
                    confidence=0.9,
                    action_required=False,
                    reason="Email intent detected, but recipient is missing.",
                )

        return decision

    def _has_recipient(self, question: str) -> bool:
        query = question.lower()
        return "@" in query or "to " in query