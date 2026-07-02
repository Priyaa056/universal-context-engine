from fastapi.testclient import TestClient

from main import app
from api.retrieval import get_retrieval_service


class DummyRetrievalService:
    def search(self, question: str, top_k: int = 5):
        assert question == "What framework is used for backend?"
        assert top_k == 2
        return [
            {
                "document_name": "UCE.pdf",
                "chunk_index": 2,
                "score": 0.91,
                "text": "FastAPI is used for backend.",
            }
        ]

    def health_check(self):
        return {
            "status": "healthy",
            "embedding_service": "available",
            "vector_store": "available",
            "retriever": "available",
        }


def test_retrieval_search_endpoint_returns_results():
    app.dependency_overrides[get_retrieval_service] = lambda: DummyRetrievalService()

    with TestClient(app) as client:
        response = client.post(
            "/api/retrieval/search",
            json={"question": "What framework is used for backend?", "top_k": 2},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["results"][0]["document_name"] == "UCE.pdf"
    assert payload["results"][0]["score"] == 0.91
    assert payload["results"][0]["text"] == "FastAPI is used for backend."


def test_retrieval_health_endpoint_returns_status():
    app.dependency_overrides[get_retrieval_service] = lambda: DummyRetrievalService()

    with TestClient(app) as client:
        response = client.get("/api/retrieval/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["retriever"] == "available"
