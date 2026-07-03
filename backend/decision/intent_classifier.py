from .models import IntentType, DecisionResult


class IntentClassifier:
    """
    Rule-based intent classifier.
    Determines what action the system should take
    based on the user's question.
    """

    def classify(self, question: str) -> DecisionResult:
        if question is None or not question.strip():
            return DecisionResult(
                intent=IntentType.CLARIFY,
                confidence=1.0,
                action_required=False,
                reason="Empty question received."
            )

        query = question.lower()
        
        if any(word in query for word in ["email", "mail", "send"]):
            return DecisionResult(
                intent=IntentType.SEND_EMAIL,
                confidence=0.95,
                action_required=True,
                reason="User requested email action."
            )

        if any(word in query for word in ["summarize", "summary", "brief"]):
            return DecisionResult(
                intent=IntentType.SUMMARIZE,
                confidence=0.95,
                action_required=False,
                reason="User requested summarization."
            )

 

        if any(word in query for word in ["task", "todo", "remind"]):
            return DecisionResult(
                intent=IntentType.CREATE_TASK,
                confidence=0.95,
                action_required=True,
                reason="User requested task creation."
            )

        if any(word in query for word in ["search", "find", "lookup"]):
            return DecisionResult(
                intent=IntentType.SEARCH_KNOWLEDGE,
                confidence=0.90,
                action_required=False,
                reason="User requested knowledge search."
            )

        return DecisionResult(
            intent=IntentType.ANSWER_ONLY,
            confidence=0.85,
            action_required=False,
            reason="General question detected."
        )