from abc import ABC, abstractmethod
from typing import List

from ..models import ContextChunk


class BaseRankingStrategy(ABC):
    """Abstract base class for ranking strategies.
    
    Defines the interface for all ranking strategy implementations.
    Subclasses must implement the rank() method and expose a name property.
    """

    @abstractmethod
    def rank(self, chunks: List[ContextChunk]) -> List[ContextChunk]:
        """Rank a list of context chunks.
        
        Args:
            chunks: List of ContextChunk objects to rank.
            
        Returns:
            List of ContextChunk objects in ranked order.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of this ranking strategy.
        
        Returns:
            String identifier for the strategy (e.g., "similarity", "mmr", "rrf").
        """
        pass
