"""Port interfaces for hexagonal architecture.

These abstract base classes define the contracts for external dependencies.
Adapters implement these ports for production or testing.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class LLMPort(ABC):
    """Port for Large Language Model text generation."""

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        **options
    ) -> str:
        """
        Generate text using the LLM.

        Args:
            system_prompt: System/role instruction for the LLM
            user_prompt: User's prompt/question
            **options: Model-specific options (temperature, max_tokens, etc.)

        Returns:
            Generated text response
        """
        pass


class EmbeddingPort(ABC):
    """Port for generating text embeddings."""

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """
        Generate embedding vector for given text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        pass


class VectorStorePort(ABC):
    """Port for vector database storage and retrieval."""

    @abstractmethod
    def create_collection(self, name: str) -> Any:
        """
        Create or get a collection for storing vectors.

        Args:
            name: Collection name

        Returns:
            Collection object (implementation-specific)
        """
        pass

    @abstractmethod
    def add_chunks(
        self,
        collection: Any,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """
        Add document chunks with embeddings to collection.

        Args:
            collection: Collection object from create_collection()
            documents: List of document text chunks
            embeddings: List of embedding vectors
            metadatas: List of metadata dicts
            ids: List of unique IDs for each chunk
        """
        pass

    @abstractmethod
    def query(
        self,
        collection: Any,
        query_embedding: List[float],
        n_results: int
    ) -> List[str]:
        """
        Query collection for most similar documents.

        Args:
            collection: Collection object
            query_embedding: Query vector
            n_results: Number of results to return

        Returns:
            List of matching document texts
        """
        pass