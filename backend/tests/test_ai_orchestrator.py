from core.orchestrator import AIOrchestrator
from core.models import WorkflowRequest, WorkflowStatus
from context.models import FormattedContext, ContextStatistics


class FakeRetriever:
    def retrieve(self, question, top_k=5):
        return [
            {
                "text": "FastAPI is used for backend.",
                "score": 0.91,
                "document_id": "doc1",
                "filename": "project.pdf",
                "chunk_index": 1,
            }
        ]


class FakeContextPipeline:
    def build(self, question, retrieved_chunks):
        return FormattedContext(
            question=question,
            context_text="FastAPI is used for backend.",
            sources=[],
            statistics=ContextStatistics(1, 0, 1, 30),
        )


class FakeResponseService:
    def generate(self, context):
        return "FastAPI is used for backend."


def test_orchestrator_accepts_valid_question():
    orchestrator = AIOrchestrator(
        retriever=FakeRetriever(),
        context_pipeline=FakeContextPipeline(),
        response_service=FakeResponseService(),
    )

    response = orchestrator.run(
        WorkflowRequest(question="What framework is used for backend?")
    )

    assert response.status == WorkflowStatus.SUCCESS
    assert "FastAPI" in response.answer