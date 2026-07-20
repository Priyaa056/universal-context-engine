from dotenv import load_dotenv

from context.models import (
    ContextStatistics,
    FormattedContext,
    SourceInfo,
)
from core.response_service import ResponseService

load_dotenv()

context = FormattedContext(
    question="What backend framework is used?",
    context_text="""
The backend of Universal Context Engine is built using FastAPI.
FastAPI is responsible for exposing REST APIs.
""",
    sources=[
        SourceInfo(
            document_id="doc1",
            filename="architecture.pdf",
            chunk_index=1,
            score=0.98,
        )
    ],
    statistics=ContextStatistics(
        total_chunks_received=1,
        duplicates_removed=0,
        final_chunks=1,
        total_context_characters=100,
    ),
)

service = ResponseService()

response = service.generate(context)

print("\n========================")
print(response)
print("========================")
