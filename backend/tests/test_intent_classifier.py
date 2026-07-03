from decision.intent_classifier import IntentClassifier
from decision.models import IntentType


def test_empty_question_returns_clarify():
    classifier = IntentClassifier()

    result = classifier.classify("")

    assert result.intent == IntentType.CLARIFY
    assert result.action_required is False


def test_summary_intent():
    classifier = IntentClassifier()

    result = classifier.classify("Summarize this document")

    assert result.intent == IntentType.SUMMARIZE
    assert result.action_required is False


def test_email_intent():
    classifier = IntentClassifier()

    result = classifier.classify("Send this summary by email")

    assert result.intent == IntentType.SEND_EMAIL
    assert result.action_required is True


def test_task_intent():
    classifier = IntentClassifier()

    result = classifier.classify("Create a task for tomorrow")

    assert result.intent == IntentType.CREATE_TASK
    assert result.action_required is True


def test_search_intent():
    classifier = IntentClassifier()

    result = classifier.classify("Find information about FastAPI")

    assert result.intent == IntentType.SEARCH_KNOWLEDGE
    assert result.action_required is False


def test_general_question_returns_answer_only():
    classifier = IntentClassifier()

    result = classifier.classify("What framework is used for backend?")

    assert result.intent == IntentType.ANSWER_ONLY
    assert result.action_required is False