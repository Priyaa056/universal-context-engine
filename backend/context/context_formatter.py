from .models import RankedContext, FormattedContext, SourceInfo, ContextStatistics


class ContextFormatter:
    """Formats ranked context into a clean context package."""

    def format(self, ranked_context: RankedContext) -> FormattedContext:
        if ranked_context is None:
            raise ValueError("Ranked context cannot be None")

        context_parts = []
        sources = []

        for index, chunk in enumerate(ranked_context.chunks, start=1):
            context_parts.append(
                f"[Chunk {index}]\n"
                f"Source: {chunk.filename} | Chunk Index: {chunk.chunk_index} | Score: {chunk.score:.4f}\n\n"
                f"{chunk.text}"
            )

            sources.append(
                SourceInfo(
                    document_id=chunk.document_id,
                    filename=chunk.filename,
                    chunk_index=chunk.chunk_index,
                    score=chunk.score,
                )
            )

        context_text = "\n\n" + ("-" * 40) + "\n\n"
        context_text = context_text.join(context_parts)

        statistics = ContextStatistics(
            total_chunks_received=len(ranked_context.chunks),
            duplicates_removed=0,
            final_chunks=len(ranked_context.chunks),
            total_context_characters=len(context_text),
        )

        return FormattedContext(
            question="",
            context_text=context_text,
            sources=sources,
            statistics=statistics,
        )