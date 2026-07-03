from context.context_formatter import ContextFormatter
from context.models import ContextChunk, RankedContext, RankingStatistics


def make_ranked_context():
    chunks = [
        ContextChunk(
            text="FastAPI is used for backend development.",
            score=0.91,
            document_id="doc1",
            filename="project.pdf",
            chunk_index=1,
        ),
        ContextChunk(
            text="Next.js is used for frontend development.",
            score=0.88,
            document_id="doc1",
            filename="project.pdf",
            chunk_index=2,
        ),
    ]

    return RankedContext(
        chunks=chunks,
        statistics=RankingStatistics(
            chunks_received=2,
            chunks_ranked=2,
            strategy_used="similarity",
        ),
    )


def test_formatter_combines_chunk_text():
    formatter = ContextFormatter()
    result = formatter.format(make_ranked_context())

    assert "FastAPI is used for backend development." in result.context_text
    assert "Next.js is used for frontend development." in result.context_text
    assert "[Chunk 1]" in result.context_text
    assert "[Chunk 2]" in result.context_text


def test_formatter_preserves_sources():
    formatter = ContextFormatter()
    result = formatter.format(make_ranked_context())

    assert len(result.sources) == 2
    assert result.sources[0].document_id == "doc1"
    assert result.sources[0].filename == "project.pdf"
    assert result.sources[0].chunk_index == 1
    assert result.sources[0].score == 0.91


def test_formatter_statistics_are_correct():
    formatter = ContextFormatter()
    result = formatter.format(make_ranked_context())

    assert result.statistics.total_chunks_received == 2
    assert result.statistics.final_chunks == 2
    assert result.statistics.total_context_characters == len(result.context_text)


def test_formatter_handles_empty_ranked_context():
    formatter = ContextFormatter()

    empty_context = RankedContext(
        chunks=[],
        statistics=RankingStatistics(
            chunks_received=0,
            chunks_ranked=0,
            strategy_used="similarity",
        ),
    )

    result = formatter.format(empty_context)

    assert result.context_text == ""
    assert result.sources == []
    assert result.statistics.final_chunks == 0


def test_formatter_rejects_none_input():
    formatter = ContextFormatter()

    try:
        formatter.format(None)
        assert False
    except ValueError:
        assert True