"""Mock adapters for testing without external dependencies."""

from typing import List, Dict, Any
from ..ports import LLMPort, EmbeddingPort, VectorStorePort


class MockLLMAdapter(LLMPort):
    """Mock LLM adapter that returns canned responses."""

    def __init__(self, canned_response: str = None):
        """
        Initialize mock LLM.

        Args:
            canned_response: Pre-defined response to return. If None, generates a simple README.
        """
        self.canned_response = canned_response or self._default_readme()
        self.call_count = 0
        self.last_system_prompt = None
        self.last_user_prompt = None

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        **options
    ) -> str:
        """Return canned response and track calls."""
        self.call_count += 1
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        return self.canned_response

    def _default_readme(self) -> str:
        """Generate a simple default README."""
        return """# Test Project

## Description
A Python project for testing README generation.

## Installation
```bash
pip install -e .
```

## Usage
```python
from test_project import main
main()
```

## Requirements
- Python >= 3.8
"""


class MockEmbeddingAdapter(EmbeddingPort):
    """Mock embedding adapter that returns fake vectors."""

    def __init__(self, embedding_dim: int = 384):
        """
        Initialize mock embedder.

        Args:
            embedding_dim: Dimension of embedding vectors
        """
        self.embedding_dim = embedding_dim
        self.call_count = 0
        self.embedded_texts = []

    def embed(self, text: str) -> List[float]:
        """Return a fake embedding based on text hash."""
        self.call_count += 1
        self.embedded_texts.append(text)

        # Generate deterministic fake embedding based on text
        # Use hash for reproducibility
        text_hash = hash(text)
        fake_embedding = [
            float((text_hash + i) % 1000) / 1000.0
            for i in range(self.embedding_dim)
        ]
        return fake_embedding


class MockVectorStoreAdapter(VectorStorePort):
    """Mock vector store using in-memory dictionary."""

    def __init__(self):
        """Initialize in-memory store."""
        self.collections = {}
        self.current_collection = None

    def create_collection(self, name: str) -> str:
        """Create in-memory collection."""
        if name not in self.collections:
            self.collections[name] = {
                'documents': [],
                'embeddings': [],
                'metadatas': [],
                'ids': []
            }
        self.current_collection = name
        return name

    def add_chunks(
        self,
        collection: Any,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """Add chunks to in-memory store."""
        coll = self.collections[collection]
        coll['documents'].extend(documents)
        coll['embeddings'].extend(embeddings)
        coll['metadatas'].extend(metadatas)
        coll['ids'].extend(ids)

    def query(
        self,
        collection: Any,
        query_embedding: List[float],
        n_results: int
    ) -> List[str]:
        """Return first n documents (simple mock - no actual similarity search)."""
        coll = self.collections[collection]
        return coll['documents'][:n_results]