from .intent_classifier import IntentClassifier
from .models import DecisionResult, IntentType


class DecisionService:
    """
    Coordinates the decision-making process.
    Uses an IntentClassifier to classify the user's request
    and applies simple decision policies.
    """

    def __init__(self, classifier: IntentClassifier):
        self.classifier = classifier

    def decide(self, question: str) -> DecisionResult:
        """
        Returns the final decision after validating
        the classifier's result.
        """
        result = self.classifier.classify(question)

        # Low confidence → ask for clarification
        if result.confidence < 0.50:
            return DecisionResult(
                intent=IntentType.CLARIFY,
                confidence=result.confidence,
                action_required=False,
                reason="Low confidence. Clarification required."
            )

        return result