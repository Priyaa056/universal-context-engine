import pytest
from core.response_service import ResponseService
from core.llm_providers import BaseLLMProvider
from context.models import (
    FormattedContext,
    SourceInfo,
    ContextStatistics,
)


class MockLLMProvider(BaseLLMProvider):
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
        self.calls = []

    def generate(self, prompt: str) -> str:
        self.calls.append(prompt)
        if self.should_fail:
            raise RuntimeError("API failure")
        return "This is a placeholder response containing FastAPI."


def test_generate_response_success():
    mock_provider = MockLLMProvider()
    service = ResponseService(provider=mock_provider)

    context = FormattedContext(
        question="Backend framework?",
        context_text="FastAPI is used for backend.",
        sources=[
            SourceInfo(
                document_id="doc1",
                filename="project.pdf",
                chunk_index=1,
                score=0.91,
            )
        ],
        statistics=ContextStatistics(
            total_chunks_received=1,
            duplicates_removed=0,
            final_chunks=1,
            total_context_characters=30,
        ),
    )

    response = service.generate(context)

    assert "placeholder" in response.lower()
    assert "FastAPI" in response
    assert len(mock_provider.calls) == 1
    assert "Backend framework?" in mock_provider.calls[0]


def test_generate_response_fallback():
    mock_provider = MockLLMProvider(should_fail=True)
    service = ResponseService(provider=mock_provider)

    context = FormattedContext(
        question="Backend framework?",
        context_text="FastAPI is used for backend.",
        sources=[],
        statistics=ContextStatistics(0, 0, 0, 0),
    )

    response = service.generate(context)
    assert "LLM unavailable." in response
    assert "FastAPI" in response


def test_none_context():
    service = ResponseService(provider=MockLLMProvider())

    with pytest.raises(ValueError):
        service.generate(None)