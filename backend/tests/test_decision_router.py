from decision.decision_router import (
    DecisionRouter,
    RouteType,
)
from decision.models import (
    DecisionResult,
    IntentType,
)


def test_answer_pipeline():
    router = DecisionRouter()

    decision = DecisionResult(
        intent=IntentType.ANSWER_ONLY,
        confidence=0.9,
        action_required=False,
        reason="General question",
    )

    result = router.route(decision)

    assert result.route == RouteType.ANSWER_PIPELINE


def test_tool_pipeline():
    router = DecisionRouter()

    decision = DecisionResult(
        intent=IntentType.SEND_EMAIL,
        confidence=0.95,
        action_required=True,
        reason="Email requested",
    )

    result = router.route(decision)

    assert result.route == RouteType.TOOL_PIPELINE


def test_search_pipeline():
    router = DecisionRouter()

    decision = DecisionResult(
        intent=IntentType.SEARCH_KNOWLEDGE,
        confidence=0.9,
        action_required=False,
        reason="Knowledge search",
    )

    result = router.route(decision)

    assert result.route == RouteType.SEARCH_PIPELINE


def test_clarification_pipeline():
    router = DecisionRouter()

    decision = DecisionResult(
        intent=IntentType.CLARIFY,
        confidence=1.0,
        action_required=False,
        reason="Need clarification",
    )

    result = router.route(decision)

    assert result.route == RouteType.CLARIFICATION_PIPELINE


def test_none_decision():
    import pytest

    router = DecisionRouter()

    with pytest.raises(ValueError):
        router.route(None)