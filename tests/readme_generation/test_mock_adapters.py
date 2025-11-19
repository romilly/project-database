"""Tests for mock adapters."""

from project_database.readme_generation.ports import LLMPort, EmbeddingPort, VectorStorePort
from project_database.readme_generation.adapters.mock_adapters import (
    MockLLMAdapter,
    MockEmbeddingAdapter,
    MockVectorStoreAdapter
)


def test_mock_llm_implements_port():
    """MockLLMAdapter should implement LLMPort."""
    adapter = MockLLMAdapter()
    assert isinstance(adapter, LLMPort)


def test_mock_llm_returns_canned_response():
    """MockLLMAdapter should return canned response."""
    custom_response = "# Custom README\nTest content"
    adapter = MockLLMAdapter(canned_response=custom_response)

    result = adapter.generate(
        system_prompt="You are a helper",
        user_prompt="Generate README",
        temperature=0.3
    )

    assert result == custom_response


def test_mock_llm_tracks_calls():
    """MockLLMAdapter should track call history."""
    adapter = MockLLMAdapter()

    assert adapter.call_count == 0

    adapter.generate("sys prompt", "user prompt")
    assert adapter.call_count == 1
    assert adapter.last_system_prompt == "sys prompt"
    assert adapter.last_user_prompt == "user prompt"

    adapter.generate("sys2", "user2")
    assert adapter.call_count == 2


def test_mock_embedding_implements_port():
    """MockEmbeddingAdapter should implement EmbeddingPort."""
    adapter = MockEmbeddingAdapter()
    assert isinstance(adapter, EmbeddingPort)


def test_mock_embedding_returns_vector():
    """MockEmbeddingAdapter should return embedding vector."""
    adapter = MockEmbeddingAdapter(embedding_dim=128)

    result = adapter.embed("test text")

    assert isinstance(result, list)
    assert len(result) == 128
    assert all(isinstance(x, float) for x in result)


def test_mock_embedding_deterministic():
    """MockEmbeddingAdapter should return same embedding for same text."""
    adapter = MockEmbeddingAdapter()

    result1 = adapter.embed("test text")
    result2 = adapter.embed("test text")

    assert result1 == result2


def test_mock_embedding_tracks_calls():
    """MockEmbeddingAdapter should track embedded texts."""
    adapter = MockEmbeddingAdapter()

    assert adapter.call_count == 0

    adapter.embed("text 1")
    adapter.embed("text 2")

    assert adapter.call_count == 2
    assert "text 1" in adapter.embedded_texts
    assert "text 2" in adapter.embedded_texts


def test_mock_vector_store_implements_port():
    """MockVectorStoreAdapter should implement VectorStorePort."""
    adapter = MockVectorStoreAdapter()
    assert isinstance(adapter, VectorStorePort)


def test_mock_vector_store_creates_collection():
    """MockVectorStoreAdapter should create collections."""
    adapter = MockVectorStoreAdapter()

    collection = adapter.create_collection("test_collection")

    assert collection == "test_collection"
    assert "test_collection" in adapter.collections


def test_mock_vector_store_adds_and_queries():
    """MockVectorStoreAdapter should store and retrieve chunks."""
    adapter = MockVectorStoreAdapter()

    collection = adapter.create_collection("test")

    # Add chunks
    documents = ["doc1", "doc2", "doc3"]
    embeddings = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
    metadatas = [{"id": 1}, {"id": 2}, {"id": 3}]
    ids = ["id1", "id2", "id3"]

    adapter.add_chunks(collection, documents, embeddings, metadatas, ids)

    # Query
    results = adapter.query(collection, [0.1, 0.2], n_results=2)

    assert len(results) == 2
    assert results[0] == "doc1"
    assert results[1] == "doc2"


def test_mock_vector_store_multiple_collections():
    """MockVectorStoreAdapter should handle multiple collections."""
    adapter = MockVectorStoreAdapter()

    coll1 = adapter.create_collection("coll1")
    coll2 = adapter.create_collection("coll2")

    adapter.add_chunks(coll1, ["doc1"], [[0.1]], [{}], ["id1"])
    adapter.add_chunks(coll2, ["doc2"], [[0.2]], [{}], ["id2"])

    results1 = adapter.query(coll1, [0.1], 1)
    results2 = adapter.query(coll2, [0.2], 1)

    assert results1[0] == "doc1"
    assert results2[0] == "doc2"