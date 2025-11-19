"""Integration tests for README generation pipeline.

These tests require:
- Ollama running on configured host
- Access to embedding and LLM models

Mark with: pytest -m integration
Skip with: pytest -m "not integration"
"""

import pytest
import os
from pathlib import Path
from dotenv import load_dotenv

from project_database.readme_generation import (
    Config,
    CodeAnalyzer,
    chunk_project
)
from project_database.readme_generation.ports import (
    LLMPort,
    EmbeddingPort,
    VectorStorePort
)
from project_database.readme_generation.adapters.ollama_adapter import (
    OllamaLLMAdapter,
    OllamaEmbeddingAdapter
)
from project_database.readme_generation.adapters.chromadb_adapter import (
    ChromaDBAdapter
)
from project_database.readme_generation.rag_pipeline import ReadmeGenerator


# Test fixtures path
FIXTURES_DIR = Path(__file__).parent / 'fixtures'


@pytest.fixture
def ollama_host():
    """Get Ollama host from environment."""
    load_dotenv()
    host = os.getenv('OLLAMA_HOST')
    if not host:
        pytest.skip("OLLAMA_HOST not set in .env file")
    return host


@pytest.fixture
def config(ollama_host):
    """Create configuration for integration tests."""
    return Config(
        ollama_host=ollama_host,
        llm_model='qwen2.5-coder:7b',
        embed_model='nomic-embed-text',
        db_path='./test_chroma_db'
    )


@pytest.fixture
def adapters(config):
    """Create real adapters for integration testing."""
    llm = OllamaLLMAdapter(config)
    embedder = OllamaEmbeddingAdapter(config)
    vector_store = ChromaDBAdapter(config)
    return llm, embedder, vector_store


@pytest.fixture
def readme_generator(config, adapters):
    """Create ReadmeGenerator with real adapters."""
    llm, embedder, vector_store = adapters
    return ReadmeGenerator(
        llm=llm,
        embedder=embedder,
        vector_store=vector_store,
        config=config
    )


@pytest.mark.integration
def test_complete_readme_generation_pipeline(readme_generator):
    """
    Integration test: Complete pipeline from code analysis to README generation.

    This tests the full flow:
    1. Analyze Python project
    2. Chunk code
    3. Generate embeddings
    4. Store in vector DB
    5. Retrieve relevant context
    6. Generate README with LLM
    """
    # 1. Analyze test project
    analyzer = CodeAnalyzer()
    project_info = analyzer.analyze_project(str(FIXTURES_DIR))

    assert project_info['file_count'] > 0
    assert project_info['total_functions'] > 0

    # 2. Chunk code
    chunks = chunk_project(project_info)
    assert len(chunks) > 0

    # 3-6. Generate README using RAG pipeline
    readme = readme_generator.generate_readme(project_info, chunks)

    # Verify README was generated
    assert readme is not None
    assert len(readme) > 0
    assert isinstance(readme, str)

    # Verify README has expected sections (basic validation)
    readme_lower = readme.lower()
    assert 'python' in readme_lower or 'project' in readme_lower

    # Should be substantial content (not just a few words)
    assert len(readme) > 100


@pytest.mark.integration
def test_ollama_llm_adapter_connectivity(config):
    """Test that we can connect to Ollama LLM."""
    llm = OllamaLLMAdapter(config)

    response = llm.generate(
        system_prompt="You are a helpful assistant.",
        user_prompt="Say 'Hello' and nothing else.",
        temperature=0.1,
        num_predict=10
    )

    assert response is not None
    assert len(response) > 0
    assert isinstance(response, str)


@pytest.mark.integration
def test_ollama_embedding_adapter_connectivity(config):
    """Test that we can generate embeddings via Ollama."""
    embedder = OllamaEmbeddingAdapter(config)

    embedding = embedder.embed("This is a test sentence.")

    assert embedding is not None
    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(isinstance(x, float) for x in embedding)


@pytest.mark.integration
def test_chromadb_adapter_storage_and_retrieval(config):
    """Test ChromaDB adapter can store and retrieve chunks."""
    vector_store = ChromaDBAdapter(config)

    # Create test collection
    collection = vector_store.create_collection("test_collection")

    # Add test chunks
    test_chunks = [
        "def hello(): return 'Hello'",
        "def goodbye(): return 'Goodbye'",
        "class TestClass: pass"
    ]
    test_embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]
    test_metadata = [
        {'type': 'function', 'name': 'hello'},
        {'type': 'function', 'name': 'goodbye'},
        {'type': 'class', 'name': 'TestClass'}
    ]
    test_ids = ['chunk_0', 'chunk_1', 'chunk_2']

    vector_store.add_chunks(
        collection=collection,
        documents=test_chunks,
        embeddings=test_embeddings,
        metadatas=test_metadata,
        ids=test_ids
    )

    # Query
    results = vector_store.query(
        collection=collection,
        query_embedding=[0.1, 0.2, 0.3],
        n_results=2
    )

    assert results is not None
    assert len(results) > 0