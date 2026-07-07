from typing import List

from ..models import ContextChunk
from .base_strategy import BaseRankingStrategy


class SimilarityRankingStrategy(BaseRankingStrategy):
    """Ranking strategy that sorts chunks by similarity score."""

    def rank(self, chunks: List[ContextChunk]) -> List[ContextChunk]:
        return sorted(chunks, key=lambda chunk: chunk.score, reverse=True)

    @property
    def name(self) -> str:
        return "similarity"