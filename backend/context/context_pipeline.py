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
        self.filter = ContextFilter()
        self.ranker = RankingService(SimilarityRankingStrategy())
        self.formatter = ContextFormatter()

    def build(self, question: str, retrieved_chunks):
        """
        Builds formatted context from retrieved chunks.

        NOTE:
        Retriever integration will be added in the next step.
        """

        context = self.builder.build(question, retrieved_chunks)

        filtered = self.filter.filter(retrieved_chunks)

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