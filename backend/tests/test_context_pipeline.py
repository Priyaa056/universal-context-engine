from context.context_pipeline import ContextPipeline


def test_context_pipeline_builds_formatted_context():
    pipeline = ContextPipeline()

    retrieved_chunks = [
        {
            "text": "FastAPI is used for backend development.",
            "score": 0.91,
            "document_id": "doc1",
            "filename": "project.pdf",
            "chunk_index": 1,
        },
        {
            "text": "Next.js is used for frontend development.",
            "score": 0.88,
            "document_id": "doc1",
            "filename": "project.pdf",
            "chunk_index": 2,
        },
    ]

    result = pipeline.build(
        question="What framework is used for backend?",
        retrieved_chunks=retrieved_chunks,
    )

    assert "FastAPI is used for backend development." in result.context_text
    assert len(result.sources) == 2
    assert result.statistics.final_chunks == 2


def test_context_pipeline_filters_low_score_chunks():
    pipeline = ContextPipeline()

    retrieved_chunks = [
        {
            "text": "Relevant chunk.",
            "score": 0.91,
            "document_id": "doc1",
            "filename": "project.pdf",
            "chunk_index": 1,
        },
        {
            "text": "Weak chunk.",
            "score": 0.20,
            "document_id": "doc1",
            "filename": "project.pdf",
            "chunk_index": 2,
        },
    ]

    result = pipeline.build(
        question="Test question",
        retrieved_chunks=retrieved_chunks,
    )

    assert "Relevant chunk." in result.context_text
    assert "Weak chunk." not in result.context_text
    assert len(result.sources) == 1