from core.response_service import ResponseService
from context.models import (
    FormattedContext,
    SourceInfo,
    ContextStatistics,
)


def test_generate_response():

    service = ResponseService()

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


def test_none_context():

    import pytest

    service = ResponseService()

    with pytest.raises(ValueError):
        service.generate(None)