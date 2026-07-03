from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class ContextChunk:
    text: str
    score: float
    document_id: str
    filename: str
    chunk_index: int


@dataclass(frozen=True)
class ContextStatistics:
    total_chunks_received: int
    duplicates_removed: int
    final_chunks: int
    total_context_characters: int


@dataclass(frozen=True)
class ContextObject:
    question: str
    chunks: List[ContextChunk] = field(default_factory=list)
    statistics: ContextStatistics = field(default_factory=lambda: ContextStatistics(0, 0, 0, 0))


@dataclass(frozen=True)
class RankingStatistics:
    chunks_received: int
    chunks_ranked: int
    strategy_used: str


@dataclass(frozen=True)
class RankedContext:
    chunks: List[ContextChunk] = field(default_factory=list)
    statistics: RankingStatistics = field(default_factory=lambda: RankingStatistics(0, 0, ""))

@dataclass(frozen=True)
class SourceInfo:
    document_id: str
    filename: str
    chunk_index: int
    score: float


@dataclass(frozen=True)
class FormattedContext:
    question: str
    context_text: str
    sources: List[SourceInfo] = field(default_factory=list)
    statistics: ContextStatistics = field(
        default_factory=lambda: ContextStatistics(0, 0, 0, 0)
    )