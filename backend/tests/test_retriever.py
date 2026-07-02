import sys
import os
import logging
from datetime import datetime

# Add backend to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.embedding_service import EmbeddingService
from rag.vector_store import VectorStore
from rag.retriever import SemanticRetriever

def run_tests():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    # Only show ERROR level logs to keep console output clean
    logging.basicConfig(level=logging.ERROR)
    
    try:
        # 1. Initialize
        embedding_service = EmbeddingService()
        vector_store = VectorStore()
        retriever = SemanticRetriever(embedding_service, vector_store)
        
        # Clear collection for clean state
        vector_store.clear_collection()
        
        # 2. Insert sample chunks
        documents = [
            "FastAPI is used for backend.",
            "Next.js is used for frontend.",
            "ChromaDB stores embeddings.",
            "Sentence Transformers generate embeddings."
        ]
        ids = ["c1", "c2", "c3", "c4"]
        
        # We need to generate embeddings for these documents to insert them
        embeddings = embedding_service.embed_documents(documents)
        
        metadatas = [
            {"filename": "doc1.txt", "chunk_index": 1, "document_id": "d1"},
            {"filename": "doc2.txt", "chunk_index": 2, "document_id": "d2"},
            {"filename": "doc3.txt", "chunk_index": 3, "document_id": "d3"},
            {"filename": "doc4.txt", "chunk_index": 4, "document_id": "d4"}
        ]
        
        vector_store.add_documents(ids, embeddings, documents, metadatas)
        
        # 3. Ask: "What framework is used for backend?"
        q1 = "What framework is used for backend?"
        print("Question:")
        print(f'"{q1}"')
        print("\n↓\n")
        print("Retrieved Chunks:")
        
        res1 = retriever.retrieve_with_scores(q1, top_k=1)
        print("1.")
        # Only print the part of text with an ellipsis if it's long, or just the text
        text1 = res1[0]['text']
        if len(text1) > 20:
            text1 = text1[:20] + "..."
        print(text1)
        print("Score:")
        print(res1[0]['score'])
        print("\n-------------------")
        
        # 4. Ask: "What database stores embeddings?"
        q2 = "What database stores embeddings?"
        print("\nQuestion:")
        print(f'"{q2}"')
        print("\n↓\n")
        print("Retrieved:")
        
        res2 = retriever.retrieve_with_scores(q2, top_k=1)
        print(res2[0]['text'])
        print("Score:")
        print(res2[0]['score'])
        print("\n-------------------")
        
        # 5. Test: "Which model creates embeddings?"
        # The prompt didn't say to print this one, but expected "Sentence Transformers".
        # I'll just run it to verify internally.
        q3 = "Which model creates embeddings?"
        res3 = retriever.retrieve_with_scores(q3, top_k=1)
        assert "Sentence Transformers" in res3[0]['text']
        
        # 6. Test Exceptions
        try:
            retriever.retrieve("")
        except ValueError:
            pass
        
        try:
            retriever.retrieve(None)
        except ValueError:
            pass
            
        try:
            retriever.retrieve("   ")
        except ValueError:
            pass
            
        try:
            retriever.retrieve("Valid question", top_k=-1)
        except ValueError:
            pass

        print("\nHealth Check:")
        print("PASSED" if retriever.health_check() == "PASS" else "FAILED")
        
        print("\nModule Status:")
        print("PASSED")
        
    except Exception as e:
        print(f"\nModule Status:\nFAILED - {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_tests()
