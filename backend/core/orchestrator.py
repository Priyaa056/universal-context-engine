from rag.embedding_service import EmbeddingService
from rag.vector_store import VectorStore
from rag.retriever import SemanticRetriever

from context.context_pipeline import ContextPipeline

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
    def __init__(self, retriever=None, context_pipeline=None, response_service=None):
        if retriever is None:
            embedding_service = EmbeddingService()
            vector_store = VectorStore()
            retriever = SemanticRetriever(embedding_service, vector_store)

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

        retrieved_chunks = self.retriever.retrieve(question, top_k=5)
        formatted_context = self.context_pipeline.build(question, retrieved_chunks)

        if route.route == RouteType.ANSWER_PIPELINE:
            answer = self.response_service.generate(formatted_context)
            tool_result = None

        elif route.route == RouteType.TOOL_PIPELINE:
            tool_result = self.tool_executor.execute(
                ToolInput(
                    tool_type=ToolType.EMAIL,
                    payload={
                        "recipient": "demo@example.com",
                        "subject": "Universal Context Engine Summary",
                        "body": formatted_context.context_text,
                    },
                )
            )
            answer = tool_result.message

        else:
            answer = f"Route selected: {route.route.value}"
            tool_result = None

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