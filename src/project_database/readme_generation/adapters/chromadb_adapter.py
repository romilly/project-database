"""ChromaDB adapter for vector storage."""

import chromadb
from typing import List, Dict, Any
from ..ports import VectorStorePort
from ..config import Config


class ChromaDBAdapter(VectorStorePort):
    """Adapter for ChromaDB vector storage."""

    def __init__(self, config: Config):
        """
        Initialize ChromaDB adapter.

        Args:
            config: Configuration with db_path
        """
        self.client = chromadb.PersistentClient(path=config.db_path)

    def create_collection(self, name: str) -> chromadb.Collection:
        """
        Create or get ChromaDB collection.

        Args:
            name: Collection name

        Returns:
            ChromaDB collection object
        """
        # Delete existing collection if it exists
        try:
            self.client.delete_collection(name)
        except:
            pass

        collection = self.client.create_collection(
            name=name,
            metadata={"description": f"Code chunks for {name}"}
        )

        return collection

    def add_chunks(
        self,
        collection: chromadb.Collection,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """
        Add document chunks to ChromaDB collection.

        Args:
            collection: ChromaDB collection
            documents: Document texts
            embeddings: Embedding vectors
            metadatas: Metadata dicts
            ids: Unique IDs
        """
        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

    def query(
        self,
        collection: chromadb.Collection,
        query_embedding: List[float],
        n_results: int
    ) -> List[str]:
        """
        Query ChromaDB for similar documents.

        Args:
            collection: ChromaDB collection
            query_embedding: Query vector
            n_results: Number of results

        Returns:
            List of matching document texts
        """
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        return results['documents'][0]