from config import get_settings

from rag.embedding_service import EmbeddingService
from rag.vector_store import VectorStore
from rag.retriever import SemanticRetriever

from context.context_pipeline import ContextPipeline
from context.models import ContextChunk

from decision.decision_service import DecisionService
from decision.intent_classifier import IntentClassifier
from decision.decision_router import DecisionRouter, RouteType

from mcp.registry import ToolRegistry
from mcp.executor import ToolExecutor
from mcp.mock_email_tool import MockEmailTool
from mcp.models import ToolInput, ToolType

from core.response_service import ResponseService
from core.models import WorkflowRequest, WorkflowResponse, WorkflowStatus


class AIOrchestrator:
    def __init__(
        self,
        retriever=None,
        context_pipeline=None,
        response_service=None,
    ):
        if retriever is None:
            settings = get_settings()

        embedding_service = EmbeddingService(
        provider_name=settings.EMBEDDING_PROVIDER,
        model_name=settings.EMBEDDING_MODEL_NAME,
        )

        vector_store = VectorStore(
        persist_directory=settings.CHROMA_PERSIST_DIR,
        )

        retriever = SemanticRetriever(
        embedding_service,
        vector_store,
        )

        self.retriever = retriever
        self.context_pipeline = context_pipeline or ContextPipeline()
        self.response_service = response_service or ResponseService()
        self.decision_service = DecisionService(IntentClassifier())
        self.decision_router = DecisionRouter()

        registry = ToolRegistry()
        registry.register(MockEmailTool())
        self.tool_executor = ToolExecutor(registry)

    def run(self, request: WorkflowRequest) -> WorkflowResponse:
        if request is None or not request.question.strip():
            return WorkflowResponse(
                status=WorkflowStatus.NEEDS_CLARIFICATION,
                answer="Please provide a valid question.",
                metadata={"reason": "empty_question"},
            )

        question = request.question.strip()

        decision = self.decision_service.decide(question)
        route = self.decision_router.route(decision)

        retrieved_raw_chunks = self.retriever.retrieve_with_scores(
            question=question,
            top_k=5,
        )

        retrieved_chunks: list[ContextChunk] = []

        for chunk in retrieved_raw_chunks:
            if isinstance(chunk, dict):
                text = str(
                    chunk.get("text")
                    or chunk.get("content")
                    or ""
                ).strip()

                if not text:
                    continue

                retrieved_chunks.append(
                    ContextChunk(
                        text=text,
                        score=float(chunk.get("score", 0.0)),
                        document_id=str(chunk.get("document_id", "")),
                        filename=str(
                            chunk.get("document_name")
                            or chunk.get("filename")
                            or "Unknown"
                        ),
                        chunk_index=int(chunk.get("chunk_index", 0)),
                    )
                )

            else:
                text = str(getattr(chunk, "text", "")).strip()

                if not text:
                    continue

                retrieved_chunks.append(
                    ContextChunk(
                        text=text,
                        score=float(getattr(chunk, "score", 0.0)),
                        document_id=str(
                            getattr(chunk, "document_id", "")
                        ),
                        filename=str(
                            getattr(
                                chunk,
                                "filename",
                                getattr(chunk, "document_name", "Unknown"),
                            )
                        ),
                        chunk_index=int(
                            getattr(chunk, "chunk_index", 0)
                        ),
                    )
                )

        print("CHAT DEBUG - retrieved chunks:", len(retrieved_chunks))

        formatted_context = self.context_pipeline.build(
            question,
            retrieved_chunks,
        )

        print(
            "CHAT DEBUG - context length:",
            len(formatted_context.context_text),
        )

        return WorkflowResponse(
            status=WorkflowStatus.SUCCESS,
            answer=answer,
            metadata={
                "question": question,
                "intent": decision.intent.value,
                "route": route.route.value,
                "sources": [
                    {
                        "filename": source.filename,
                        "chunk_index": source.chunk_index,
                        "score": source.score,
                    }
                    for source in formatted_context.sources
                ],
                "tool_result": tool_result.data if tool_result else None,
            },
        )