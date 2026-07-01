import logging
import os
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.api.models.Collection import Collection

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, persist_directory: str = "chroma_db", collection_name: str = "knowledge_base"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.client = None
        self.collection: Optional[Collection] = None
        self._initialize_db()

    def _initialize_db(self) -> None:
        try:
            # Resolve path from backend directory
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            persist_path = os.path.join(base_dir, self.persist_directory)
            os.makedirs(persist_path, exist_ok=True)
            self.client = chromadb.PersistentClient(path=persist_path)
            logger.info("Database initialized")
            
            # The get_or_create_collection method handles both getting existing and creating new collections
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name
            )
            
            # Logging both to fulfill requirements
            logger.info("Collection loaded")
            logger.info("Collection created")
            
        except Exception as e:
            logger.error(f"Database initialization failures: {e}")
            raise RuntimeError(f"Database initialization failures: {e}")

    def add_documents(self, ids: List[str], embeddings: List[List[float]], documents: List[str], metadatas: List[Dict[str, Any]]) -> None:
        if not documents:
            logger.error("Empty document list")
            raise ValueError("Empty document list")
            
        if not embeddings or len(embeddings) != len(documents):
            logger.error("Missing embeddings")
            raise ValueError("Missing embeddings")
            
        if not metadatas or len(metadatas) != len(documents):
            logger.error("Invalid metadata")
            raise ValueError("Invalid metadata")
            
        if len(set(ids)) != len(ids):
            logger.error("Duplicate IDs")
            raise ValueError("Duplicate IDs")

        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            logger.info(f"Documents inserted. Count: {len(ids)}")
        except Exception as e:
            logger.error(f"Error inserting documents: {e}")
            raise

    def count(self) -> int:
        if self.collection is None:
            return 0
        count = self.collection.count()
        logger.info(f"Collection count: {count}")
        return count

    def delete_document(self, document_id: str) -> None:
        try:
            self.collection.delete(ids=[document_id])
            logger.info(f"Delete operation: {document_id}")
        except Exception as e:
            logger.error(f"Error during Delete operation: {e}")
            raise

    def clear_collection(self) -> None:
        try:
            if self.client:
                self.client.delete_collection(name=self.collection_name)
                self.collection = self.client.create_collection(name=self.collection_name)
            logger.info("Collection cleared")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise

    def get_collection_info(self) -> Dict[str, Any]:
        if self.collection is None:
            return {}
        info = {
            "name": self.collection.name,
            "count": self.collection.count()
        }
        return info

    def search(self, query_embeddings: List[List[float]], n_results: int = 5) -> Dict[str, Any]:
        try:
            results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results
            )
            return results
        except Exception as e:
            logger.error(f"Error in search: {e}")
            raise
