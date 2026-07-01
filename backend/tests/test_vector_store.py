import sys
import os
import logging
from datetime import datetime

# Add backend to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.vector_store import VectorStore

def run_test():
    # Set up basic logging to only show errors so prints are clean
    logging.basicConfig(level=logging.ERROR)
    
    try:
        store = VectorStore()
        
        # Ensure a clean state
        store.clear_collection()
        
        # Insert 3 sample embeddings
        ids = ["doc1", "doc2", "doc3"]
        embeddings = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
        documents = ["This is document 1", "This is document 2", "This is document 3"]
        metadatas = [
            {"document_id": "id1", "filename": "f1.txt", "chunk_index": 0, "upload_time": datetime.now().isoformat()},
            {"document_id": "id2", "filename": "f2.txt", "chunk_index": 0, "upload_time": datetime.now().isoformat()},
            {"document_id": "id3", "filename": "f3.txt", "chunk_index": 0, "upload_time": datetime.now().isoformat()}
        ]
        
        store.add_documents(ids, embeddings, documents, metadatas)
        
        # Retrieve collection info
        info = store.get_collection_info()
        print("Collection Name:")
        print(info.get("name"))
        
        print("Collection Count:")
        print(store.count())
        
        # Delete one document
        store.delete_document("doc2")
        print("After Delete:")
        print(store.count())
        
        # Clear collection
        store.clear_collection()
        print("After Clear:")
        print(store.count())
        
        print("Module Status:")
        print("PASSED")
        
    except Exception as e:
        print("Module Status:")
        print("FAILED")
        print(str(e))

if __name__ == "__main__":
    run_test()
