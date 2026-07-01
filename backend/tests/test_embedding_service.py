import sys
import time
from pathlib import Path

# Add backend directory to path so we can import from rag
backend_dir = str(Path(__file__).resolve().parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from rag.embedding_service import EmbeddingService

def run_tests():
    print("=========================================================")
    print("STARTING EMBEDDING SERVICE TESTS")
    print("=========================================================")
    print()

    try:
        # ---------------------------------------------------------
        # Test 1: Initialize EmbeddingService
        # ---------------------------------------------------------
        print("Running Test 1: Initialize EmbeddingService...")
        t0 = time.perf_counter()
        # We explicitly set the provider for testing
        service = EmbeddingService(provider_name="sentence-transformers")
        t1 = time.perf_counter()
        
        print("-" * 37)
        print("Embedding Provider")
        print(service.provider_name)
        print("Model")
        print(service.model_name)
        print("-" * 37)
        print(f"Initialization took: {(t1 - t0) * 1000:.2f} ms")
        print()

        # ---------------------------------------------------------
        # Test 2: Embed single text
        # ---------------------------------------------------------
        print("Running Test 2: Embed single text...")
        test_text = "FastAPI is used for backend development."
        t0 = time.perf_counter()
        embedding = service.embed_text(test_text)
        t1 = time.perf_counter()
        
        print("-" * 37)
        print("Embedding Dimension")
        print(len(embedding))
        print("First five values")
        print([round(v, 4) for v in embedding[:5]])
        print("-" * 37)
        print(f"Execution Time")
        print(f"{(t1 - t0) * 1000:.2f} ms")
        print("-" * 37)
        print()

        # ---------------------------------------------------------
        # Test 3: Batch embeddings
        # ---------------------------------------------------------
        print("Running Test 3: Batch embeddings...")
        batch_texts = [
            "FastAPI Backend",
            "Next.js Frontend",
            "ChromaDB Vector Database"
        ]
        t0 = time.perf_counter()
        embeddings = service.embed_documents(batch_texts)
        t1 = time.perf_counter()
        
        print("-" * 37)
        print("Batch Size")
        print(len(embeddings))
        print("Dimension of each embedding")
        print([len(emb) for emb in embeddings])
        print("-" * 37)
        print(f"Execution Time")
        print(f"{(t1 - t0) * 1000:.2f} ms")
        print("-" * 37)
        print()

        # ---------------------------------------------------------
        # Test 4: Embed empty string
        # ---------------------------------------------------------
        print("Running Test 4: Embed empty string...")
        empty_embedding = service.embed_text("")
        assert len(empty_embedding) == 0, "Empty string should return empty list"
        print("Graceful handling of empty string verified.")
        print()

        # ---------------------------------------------------------
        # Test 5: Embed None
        # ---------------------------------------------------------
        print("Running Test 5: Embed None...")
        try:
            service.embed_text(None)
            assert False, "embed_text(None) should have raised ValueError"
        except ValueError as e:
            print("Proper validation for None verified.")
        print()
        
        # Also verify OpenAI and Gemini raise NotImplementedError
        from rag.embedding_factory import get_embedding_provider
        
        print("Running Test 6: Verify OpenAI placeholder...")
        try:
            openai_provider = get_embedding_provider("openai", "text-embedding-3-small")
            openai_provider.embed_text("test")
            assert False, "OpenAI should have raised NotImplementedError"
        except NotImplementedError:
            print("OpenAI placeholder verified.")
            
        print("Running Test 7: Verify Gemini placeholder...")
        try:
            gemini_provider = get_embedding_provider("gemini", "models/text-embedding-004")
            gemini_provider.embed_text("test")
            assert False, "Gemini should have raised NotImplementedError"
        except NotImplementedError:
            print("Gemini placeholder verified.")
        print()

        print("=========================================================")
        print("Module Status")
        print("PASSED")
        print("=========================================================")

    except Exception as e:
        print("\n=========================================================")
        print("Module Status")
        print(f"FAILED: {e}")
        print("=========================================================")
        raise

if __name__ == "__main__":
    run_tests()
