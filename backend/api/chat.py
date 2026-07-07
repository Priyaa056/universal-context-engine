from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from core.orchestrator import AIOrchestrator
from core.models import WorkflowRequest

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    status: str
    answer: str
    metadata: dict


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        orchestrator = AIOrchestrator()
        result = orchestrator.run(
            WorkflowRequest(question=request.question)
        )

        return ChatResponse(
            status=result.status.value,
            answer=result.answer,
            metadata=result.metadata,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))