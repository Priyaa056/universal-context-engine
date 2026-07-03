import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from context.models import ContextChunk
from context.ranking import RankingService, SimilarityRankingStrategy
from context.exceptions import ContextBuilderError


def make_chunk(text, score, document_id="doc-1", filename="file.txt", chunk_index=0):
    """Helper to create a ContextChunk."""
    return ContextChunk(
        text=text,
        score=score,
        document_id=document_id,
        filename=filename,
        chunk_index=chunk_index,
    )


def make_chunk_dict(text, score, document_id="doc-1", filename="file.txt", chunk_index=0):
    """Helper to create a chunk dictionary."""
    return {
        "text": text,
        "score": score,
        "document_id": document_id,
        "filename": filename,
        "chunk_index": chunk_index,
    }


# ========================
# Similarity Strategy Tests
# ========================


class TestSimilarityRankingStrategy:
    """Tests for SimilarityRankingStrategy."""

    def test_strategy_name_is_correct(self):
        """Test that strategy exposes correct name."""
        strategy = SimilarityRankingStrategy()
        assert strategy.name == "similarity"

    def test_similarity_ranking_sorts_by_score_descending(self):
        """Test that chunks are sorted by score (highest first)."""
        strategy = SimilarityRankingStrategy()
        chunks = [
            make_chunk("Low relevance", 0.5),
            make_chunk("High relevance", 0.9),
            make_chunk("Medium relevance", 0.7),
        ]

        ranked = strategy.rank(chunks)

        assert len(ranked) == 3
        assert ranked[0].score == 0.9
        assert ranked[1].score == 0.7
        assert ranked[2].score == 0.5

    def test_similarity_ranking_preserves_metadata(self):
        """Test that all metadata is preserved during ranking."""
        strategy = SimilarityRankingStrategy()
        chunks = [
            make_chunk("Text A", 0.5, document_id="doc-1", filename="a.txt", chunk_index=0),
            make_chunk("Text B", 0.9, document_id="doc-2", filename="b.txt", chunk_index=5),
            make_chunk("Text C", 0.7, document_id="doc-3", filename="c.txt", chunk_index=10),
        ]

        ranked = strategy.rank(chunks)

        # Verify highest score chunk (Text B) has correct metadata
        assert ranked[0].text == "Text B"
        assert ranked[0].score == 0.9
        assert ranked[0].document_id == "doc-2"
        assert ranked[0].filename == "b.txt"
        assert ranked[0].chunk_index == 5

    def test_similarity_ranking_handles_empty_list(self):
        """Test that empty chunk list is handled gracefully."""
        strategy = SimilarityRankingStrategy()
        ranked = strategy.rank([])
        assert ranked == []

    def test_similarity_ranking_handles_single_chunk(self):
        """Test that single chunk is returned as-is."""
        strategy = SimilarityRankingStrategy()
        chunk = make_chunk("Only chunk", 0.8)
        ranked = strategy.rank([chunk])
        assert len(ranked) == 1
        assert ranked[0] == chunk

    def test_similarity_ranking_handles_identical_scores(self):
        """Test that chunks with identical scores are preserved."""
        strategy = SimilarityRankingStrategy()
        chunks = [
            make_chunk("First", 0.8),
            make_chunk("Second", 0.8),
            make_chunk("Third", 0.8),
        ]

        ranked = strategy.rank(chunks)

        assert len(ranked) == 3
        assert all(chunk.score == 0.8 for chunk in ranked)


# ========================
# Ranking Service Tests
# ========================


class TestRankingService:
    """Tests for RankingService with dependency injection."""

    def test_service_initialization_with_valid_strategy(self):
        """Test that service initializes with a valid strategy."""
        strategy = SimilarityRankingStrategy()
        service = RankingService(strategy)
        assert service is not None

    def test_service_initialization_rejects_none_strategy(self):
        """Test that service rejects None strategy."""
        with pytest.raises(ContextBuilderError, match="Strategy cannot be None"):
            RankingService(None)

    def test_service_initialization_rejects_non_strategy_object(self):
        """Test that service rejects non-strategy object."""
        with pytest.raises(ContextBuilderError, match="Strategy must be an instance of BaseRankingStrategy"):
            RankingService("not a strategy")

    def test_service_ranks_chunk_dictionaries(self):
        """Test that service can rank chunk dictionaries."""
        service = RankingService(SimilarityRankingStrategy())
        chunks = [
            make_chunk_dict("Low relevance", 0.4),
            make_chunk_dict("High relevance", 0.9),
            make_chunk_dict("Medium relevance", 0.7),
        ]

        result = service.rank(chunks)

        assert len(result.chunks) == 3
        assert result.chunks[0].score == 0.9
        assert result.chunks[1].score == 0.7
        assert result.chunks[2].score == 0.4

    def test_service_ranks_context_chunks(self):
        """Test that service can rank ContextChunk objects."""
        service = RankingService(SimilarityRankingStrategy())
        chunks = [
            make_chunk("Low relevance", 0.4),
            make_chunk("High relevance", 0.9),
            make_chunk("Medium relevance", 0.7),
        ]

        result = service.rank(chunks)

        assert len(result.chunks) == 3
        assert result.chunks[0].score == 0.9

    def test_service_preserves_metadata_during_ranking(self):
        """Test that metadata is preserved through ranking service."""
        service = RankingService(SimilarityRankingStrategy())
        chunks = [
            make_chunk_dict("Text A", 0.5, document_id="doc-1", filename="a.txt", chunk_index=0),
            make_chunk_dict("Text B", 0.9, document_id="doc-2", filename="b.txt", chunk_index=5),
        ]

        result = service.rank(chunks)

        # Highest score should be first
        assert result.chunks[0].document_id == "doc-2"
        assert result.chunks[0].filename == "b.txt"
        assert result.chunks[0].chunk_index == 5

    def test_service_rejects_none_chunks(self):
        """Test that service rejects None chunks input."""
        service = RankingService(SimilarityRankingStrategy())
        with pytest.raises(ContextBuilderError, match="Chunks cannot be None"):
            service.rank(None)

    def test_service_rejects_non_list_chunks(self):
        """Test that service rejects non-list chunks input."""
        service = RankingService(SimilarityRankingStrategy())
        with pytest.raises(ContextBuilderError, match="Chunks must be a list"):
            service.rank("not a list")

    def test_service_handles_empty_chunk_list(self):
        """Test that service handles empty chunk list gracefully."""
        service = RankingService(SimilarityRankingStrategy())
        result = service.rank([])

        assert result.chunks == []
        assert result.statistics.chunks_received == 0
        assert result.statistics.chunks_ranked == 0

    def test_service_statistics_track_chunk_counts(self):
        """Test that statistics correctly track chunk counts."""
        service = RankingService(SimilarityRankingStrategy())
        chunks = [
            make_chunk_dict("One", 0.8),
            make_chunk_dict("Two", 0.7),
            make_chunk_dict("Three", 0.6),
        ]

        result = service.rank(chunks)

        assert result.statistics.chunks_received == 3
        assert result.statistics.chunks_ranked == 3

    def test_service_statistics_track_strategy_used(self):
        """Test that statistics track which strategy was used."""
        service = RankingService(SimilarityRankingStrategy())
        chunks = [make_chunk_dict("Test", 0.8)]

        result = service.rank(chunks)

        assert result.statistics.strategy_used == "similarity"

    def test_service_output_structure(self):
        """Test that service returns properly structured RankedContext."""
        service = RankingService(SimilarityRankingStrategy())
        chunks = [
            make_chunk_dict("Text A", 0.5),
            make_chunk_dict("Text B", 0.9),
        ]

        result = service.rank(chunks)

        assert hasattr(result, "chunks")
        assert hasattr(result, "statistics")
        assert hasattr(result.statistics, "chunks_received")
        assert hasattr(result.statistics, "chunks_ranked")
        assert hasattr(result.statistics, "strategy_used")

    def test_service_normalizes_mixed_input_types(self):
        """Test that service handles mixed chunk types (dict and ContextChunk)."""
        service = RankingService(SimilarityRankingStrategy())
        chunks = [
            make_chunk_dict("Dict chunk", 0.8),
            make_chunk("Context chunk", 0.9),
        ]

        result = service.rank(chunks)

        assert len(result.chunks) == 2
        assert isinstance(result.chunks[0], ContextChunk)
        assert isinstance(result.chunks[1], ContextChunk)

    def test_service_handles_chunks_with_missing_fields(self):
        """Test that service handles chunks with missing optional fields."""
        service = RankingService(SimilarityRankingStrategy())
        chunks = [
            {"text": "Only text"},
            {"text": "Text with score", "score": 0.9},
        ]

        result = service.rank(chunks)

        assert len(result.chunks) == 2
        # After ranking by similarity (descending), 0.9 score is first
        assert result.chunks[0].score == 0.9
        assert result.chunks[1].score == 0.0  # Default


# ========================
# Integration Tests
# ========================


class TestRankingIntegration:
    """Integration tests for ranking workflow."""

    def test_ranking_workflow_full_pipeline(self):
        """Test complete ranking workflow: input -> service -> output."""
        service = RankingService(SimilarityRankingStrategy())
        chunks = [
            make_chunk_dict("First", 0.6, document_id="doc-1"),
            make_chunk_dict("Second", 0.9, document_id="doc-2"),
            make_chunk_dict("Third", 0.7, document_id="doc-3"),
        ]

        result = service.rank(chunks)

        # Verify correct ranking order
        assert result.chunks[0].text == "Second"
        assert result.chunks[0].document_id == "doc-2"
        assert result.chunks[1].text == "Third"
        assert result.chunks[2].text == "First"

        # Verify statistics
        assert result.statistics.chunks_received == 3
        assert result.statistics.chunks_ranked == 3
        assert result.statistics.strategy_used == "similarity"

    def test_ranking_immutability_of_context_chunks(self):
        """Test that ContextChunk objects remain immutable during ranking."""
        strategy = SimilarityRankingStrategy()
        chunk = make_chunk("Test", 0.8)

        # This should not raise an error or modify chunk
        ranked = strategy.rank([chunk])

        # Original chunk should be unchanged
        assert chunk.text == "Test"
        assert chunk.score == 0.8

    def test_strategy_injection_allows_different_implementations(self):
        """Test that dependency injection allows swapping strategies."""
        chunks = [
            make_chunk_dict("A", 0.5),
            make_chunk_dict("B", 0.9),
        ]

        # Using SimilarityRankingStrategy
        service1 = RankingService(SimilarityRankingStrategy())
        result1 = service1.rank(chunks)

        assert result1.statistics.strategy_used == "similarity"
        assert result1.chunks[0].score == 0.9  # Highest first

    def test_ranking_service_with_complex_metadata(self):
        """Test ranking service preserves complex metadata scenarios."""
        service = RankingService(SimilarityRankingStrategy())
        chunks = [
            make_chunk_dict(
                "Text 1", 0.5,
                document_id="doc-uuid-12345",
                filename="complex_file_name_2024.pdf",
                chunk_index=42
            ),
            make_chunk_dict(
                "Text 2", 0.95,
                document_id="doc-uuid-67890",
                filename="another_file.txt",
                chunk_index=1
            ),
        ]

        result = service.rank(chunks)

        # Verify highest score is first with complete metadata
        highest = result.chunks[0]
        assert highest.score == 0.95
        assert highest.document_id == "doc-uuid-67890"
        assert highest.filename == "another_file.txt"
        assert highest.chunk_index == 1
