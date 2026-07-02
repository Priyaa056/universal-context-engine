from fastapi.testclient import TestClient

from api.kb import get_retriever
from main import app


class DummyRetriever:
    def retrieve_with_scores(self, question: str, top_k: int = 5):
        assert question == "What is FastAPI?"
        assert top_k == 2
        return [
            {
                "document_name": "alpha.txt",
                "chunk_index": 1,
                "score": 0.91,
                "text": "FastAPI is great.",
                "metadata": {
                    "document_id": "doc-1",
                    "filename": "alpha.txt",
                    "chunk_index": 1,
                },
            }
        ]


def test_search_endpoint_returns_structured_results():
    app.dependency_overrides[get_retriever] = lambda: DummyRetriever()

    with TestClient(app) as client:
        response = client.post(
            "/kb/search",
            json={"query": "What is FastAPI?", "n_results": 2},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "What is FastAPI?"
    assert payload["total"] == 1
    assert payload["results"][0]["document_name"] == "alpha.txt"
    assert payload["results"][0]["content"] == "FastAPI is great."
    assert payload["results"][0]["score"] == 0.91
    assert payload["results"][0]["document_id"] == "doc-1"
