from typing import Any, Dict, List, Optional

from ..exceptions import ContextBuilderError
from ..models import ContextChunk, RankedContext, RankingStatistics
from .base_strategy import BaseRankingStrategy


class RankingService:
    """Service that ranks context chunks using injected ranking strategies.
    
    Uses dependency injection to accept any ranking strategy implementing
    the BaseRankingStrategy interface.
    """

    def __init__(self, strategy: BaseRankingStrategy) -> None:
        """Initialize RankingService with a ranking strategy.
        
        Args:
            strategy: A BaseRankingStrategy implementation.
            
        Raises:
            ContextBuilderError: If strategy is None or not a BaseRankingStrategy.
        """
        if strategy is None:
            raise ContextBuilderError("Strategy cannot be None")

        if not isinstance(strategy, BaseRankingStrategy):
            raise ContextBuilderError("Strategy must be an instance of BaseRankingStrategy")

        self._strategy = strategy

    def rank(self, chunks: Optional[List[Dict[str, Any]]]) -> RankedContext:
        """Rank a list of chunks using the injected strategy.
        
        Args:
            chunks: List of chunk dictionaries to rank.
                   Can be empty list but not None.
                   
        Returns:
            RankedContext with ranked chunks and statistics.
            
        Raises:
            ContextBuilderError: If chunks is None or not a list.
        """
        self._validate_input(chunks)

        # Convert dict chunks to ContextChunk objects if needed
        context_chunks = [self._normalize_chunk(chunk) for chunk in (chunks or [])]
        chunks_received = len(context_chunks)

        # Rank using the strategy
        ranked_chunks = self._strategy.rank(context_chunks)

        # Create statistics
        statistics = RankingStatistics(
            chunks_received=chunks_received,
            chunks_ranked=len(ranked_chunks),
            strategy_used=self._strategy.name,
        )

        return RankedContext(
            chunks=ranked_chunks,
            statistics=statistics,
        )

    def _validate_input(self, chunks: Optional[List[Dict[str, Any]]]) -> None:
        """Validate input chunks.
        
        Args:
            chunks: List of chunks to validate.
            
        Raises:
            ContextBuilderError: If chunks is None or not a list.
        """
        if chunks is None:
            raise ContextBuilderError("Chunks cannot be None")

        if not isinstance(chunks, list):
            raise ContextBuilderError("Chunks must be a list")

    def _normalize_chunk(self, chunk: Dict[str, Any]) -> ContextChunk:
        """Convert a dict chunk to ContextChunk, or pass through if already ContextChunk.
        
        Args:
            chunk: Dictionary or ContextChunk object.
            
        Returns:
            ContextChunk object with all fields properly typed.
        """
        if isinstance(chunk, ContextChunk):
            return chunk

        return ContextChunk(
            text=str(chunk.get("text") or ""),
            score=float(chunk.get("score", 0.0) or 0.0),
            document_id=str(chunk.get("document_id") or ""),
            filename=str(chunk.get("filename") or ""),
            chunk_index=int(chunk.get("chunk_index", 0) or 0),
        )
