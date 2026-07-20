from typing import Optional

from .context_builder import ContextBuilder
from .context_filter import ContextFilter
from .context_formatter import ContextFormatter
from .ranking.ranking_service import RankingService
from .ranking.similarity_strategy import SimilarityRankingStrategy


class ContextPipeline:
    """
    Coordinates the complete context processing workflow.

    Current responsibilities:
    - Context Builder
    - Context Filter
    - Context Ranking
    - Context Formatting

    Future:
    - Retriever integration
    """

    def __init__(self):
        self.builder = ContextBuilder()
        self.filter = ContextFilter(minimum_score=0.25)
        self.ranker = RankingService(SimilarityRankingStrategy())
        self.formatter = ContextFormatter()

    def build(self, question: str, retrieved_chunks):
        """
        Builds formatted context from retrieved chunks.

        Accepts raw dicts (flat or with nested metadata) or ContextChunk
        objects — normalisation is handled by the ContextBuilder.
        """

        # builder normalises dicts → ContextChunk and deduplicates
        context = self.builder.build(question, retrieved_chunks)

        # filter operates on the already-normalised ContextChunks
        filtered = self.filter.filter(context.chunks)

        ranked = self.ranker.rank(
            [
                {
                    "text": chunk.text,
                    "score": chunk.score,
                    "document_id": chunk.document_id,
                    "filename": chunk.filename,
                    "chunk_index": chunk.chunk_index,
                }
                for chunk in filtered.chunks
            ]
        )

        formatted = self.formatter.format(ranked)

        return formatted