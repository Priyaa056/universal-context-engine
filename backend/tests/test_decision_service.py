from decision.decision_service import DecisionService
from decision.intent_classifier import IntentClassifier
from decision.models import IntentType


def test_decision_service_returns_answer_only():
    service = DecisionService(IntentClassifier())

    result = service.decide("What framework is used for backend?")

    assert result.intent == IntentType.ANSWER_ONLY
    assert result.action_required is False


def test_decision_service_returns_email_action():
    service = DecisionService(IntentClassifier())

    result = service.decide("Send this summary by email")

    assert result.intent == IntentType.SEND_EMAIL
    assert result.action_required is True


def test_decision_service_returns_clarify_for_empty_input():
    service = DecisionService(IntentClassifier())

    result = service.decide("")

    assert result.intent == IntentType.CLARIFY
    assert result.action_required is False


def test_decision_service_uses_injected_classifier():
    class FakeClassifier:
        def classify(self, question):
            from decision.models import DecisionResult
            return DecisionResult(
                intent=IntentType.CLARIFY,
                confidence=0.2,
                action_required=False,
                reason="Fake low confidence result",
            )

    service = DecisionService(FakeClassifier())

    result = service.decide("anything")

    assert result.intent == IntentType.CLARIFY
    assert result.confidence == 0.2