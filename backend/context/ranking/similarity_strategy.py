from typing import List

from ..models import ContextChunk
from .base_strategy import BaseRankingStrategy


class SimilarityRankingStrategy(BaseRankingStrategy):
    """Ranking strategy that sorts chunks by similarity score (highest first).
    
    This strategy preserves all chunk metadata while ordering chunks based on
    their semantic similarity score in descending order.
    """

    def rank(self, chunks: List[ContextChunk]) -> List[ContextChunk]:
        """Rank chunks by similarity score in descending order.
        
        Args:
            chunks: List of ContextChunk objects to rank.
            
        Returns:
            List of ContextChunk objects sorted by score (highest first).
        """
        return sorted(chunks, key=lambda chunk: chunk.score, reverse=True)

    @property
    def name(self) -> str:
        """Get the strategy name.
        
        Returns:
            "similarity"
        """
        return "similarity"
