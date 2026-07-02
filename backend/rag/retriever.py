import logging
from typing import List, Dict, Any

from rag.embedding_service import EmbeddingService
from rag.vector_store import VectorStore

logger = logging.getLogger(__name__)


class SemanticRetriever:
    """
    Semantic Retriever for the Universal Context Engine.
    
    Responsible solely for retrieving the most relevant document chunks
    from the VectorStore based on a semantic search of the provided question.
    """

    def __init__(self, embedding_service: EmbeddingService, vector_store: VectorStore):
        """
        Initialize the SemanticRetriever using Dependency Injection.
        """
        if embedding_service is None:
            raise ValueError("EmbeddingService cannot be None")
        if vector_store is None:
            raise ValueError("VectorStore cannot be None")
            
        self._embedding_service = embedding_service
        self._vector_store = vector_store
        logger.info("SemanticRetriever initialized with EmbeddingService and VectorStore")

    def _validate_inputs(self, question: str, top_k: int) -> None:
        """Validate search inputs."""
        if question is None:
            logger.error("None input for question")
            raise ValueError("Question cannot be None")
            
        if not isinstance(question, str):
            logger.error("Invalid question type")
            raise ValueError("Question must be a string")
            
        if not question.strip():
            logger.error("Empty or whitespace-only question")
            raise ValueError("Question cannot be empty or whitespace-only")
            
        if not isinstance(top_k, int) or top_k <= 0:
            logger.error(f"Invalid top_k: {top_k}")
            raise ValueError("top_k must be a positive integer")

    def retrieve(self, question: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a given question.
        Returns the same output as retrieve_with_scores.
        """
        return self.retrieve_with_scores(question, top_k)

    def retrieve_with_scores(self, question: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks and include similarity scores.
        """
        try:
            self._validate_inputs(question, top_k)
            logger.info(f"Question received: '{question}' (top_k={top_k})")
            
            # Generate embedding
            embedding = self._embedding_service.embed_text(question)
            logger.info("Embedding generated successfully")
            
            # Search ChromaDB via VectorStore
            logger.info("Vector search started")
            search_results = self._vector_store.search(
                query_embeddings=[embedding],
                n_results=top_k
            )
            
            # Parse results
            retrieved_chunks = []
            
            # ChromaDB returns parallel arrays inside lists (one per query)
            if search_results and "documents" in search_results and search_results["documents"]:
                documents = search_results["documents"][0]
                metadatas = search_results["metadatas"][0] if search_results.get("metadatas") else [{}] * len(documents)
                distances = search_results["distances"][0] if search_results.get("distances") else [0.0] * len(documents)
                
                for doc, meta, dist in zip(documents, metadatas, distances):
                    # Convert distance to a rough similarity score [0, 1] for typical cosine/L2
                    # Depending on Chroma config, this is an approximation.
                    score = max(0.0, 1.0 - (dist / 2.0))
                    
                    retrieved_chunks.append({
                        "document_name": meta.get("filename", "Unknown"),
                        "chunk_index": meta.get("chunk_index", 0),
                        "score": round(score, 2),
                        "text": doc,
                        "metadata": meta
                    })
            
            logger.info(f"Retrieved chunk count: {len(retrieved_chunks)}")
            logger.info(f"Similarity scores: {[chunk['score'] for chunk in retrieved_chunks]}")
            
            return retrieved_chunks
            
        except Exception as e:
            logger.error(f"Error during retrieval: {e}")
            raise

    def health_check(self) -> str:
        """
        Verify that embedding service and vector store are available.
        """
        try:
            # Check embedding service (simple test embed)
            self._embedding_service.embed_text("health")
            
            # Check vector store
            info = self._vector_store.get_collection_info()
            if not info or "name" not in info:
                return "FAIL"
                
            return "PASS"
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return "FAIL"
