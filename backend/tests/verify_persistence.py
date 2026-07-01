import sys
import os
import logging
from datetime import datetime

# Add backend to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.vector_store import VectorStore

def run_verify():
    logging.basicConfig(level=logging.ERROR)
    try:
        # 1. Initialize
        store1 = VectorStore()
        store1.clear_collection()
        
        # 2. Insert sample vectors
        ids = ["p1", "p2"]
        embeddings = [[0.1, 0.1], [0.2, 0.2]]
        documents = ["Persistence doc 1", "Persistence doc 2"]
        metadatas = [
            {"document_id": "p1", "filename": "p1.txt", "chunk_index": 0, "upload_time": datetime.now().isoformat()},
            {"document_id": "p2", "filename": "p2.txt", "chunk_index": 0, "upload_time": datetime.now().isoformat()}
        ]
        store1.add_documents(ids, embeddings, documents, metadatas)
        
        count_before = store1.count()
        collection_name = store1.get_collection_info().get("name")
        
        # 3. Simulate application restart by deleting reference and re-instantiating
        del store1
        
        store2 = VectorStore()
        count_after = store2.count()
        
        # 4. Gather paths
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        persist_path = os.path.join(base_dir, "chroma_db")
        
        print("--- RESULTS ---")
        print(f"Storage path: {persist_path}")
        print(f"Collection name: {collection_name}")
        print(f"Count before reinitialize: {count_before}")
        print(f"Count after reinitialize: {count_after}")
        
        if count_before == count_after and count_after == 2:
            print("Status: PASS")
        else:
            print("Status: FAIL")
            
    except Exception as e:
        print(f"Status: FAIL - {e}")

if __name__ == "__main__":
    run_verify()
