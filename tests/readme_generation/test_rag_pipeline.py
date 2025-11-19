"""Tests for RAG pipeline using mock adapters."""

from pathlib import Path
from project_database.readme_generation import CodeAnalyzer, chunk_project, Config
from project_database.readme_generation.adapters.mock_adapters import (
    MockLLMAdapter,
    MockEmbeddingAdapter,
    MockVectorStoreAdapter
)
from project_database.readme_generation.rag_pipeline import ReadmeGenerator


# Test fixtures path
FIXTURES_DIR = Path(__file__).parent / 'fixtures'


def test_readme_generator_initialization():
    """ReadmeGenerator should initialize with ports."""
    config = Config(ollama_host='http://localhost:11434')
    llm = MockLLMAdapter()
    embedder = MockEmbeddingAdapter()
    vector_store = MockVectorStoreAdapter()

    generator = ReadmeGenerator(
        llm=llm,
        embedder=embedder,
        vector_store=vector_store,
        config=config
    )

    assert generator is not None
    assert generator.llm == llm
    assert generator.embedder == embedder
    assert generator.vector_store == vector_store


def test_readme_generator_generates_readme():
    """ReadmeGenerator should generate README from project info and chunks."""
    config = Config(ollama_host='http://localhost:11434')
    llm = MockLLMAdapter(canned_response="# Test Project\nGenerated README")
    embedder = MockEmbeddingAdapter()
    vector_store = MockVectorStoreAdapter()

    generator = ReadmeGenerator(llm, embedder, vector_store, config)

    # Analyze and chunk test project
    analyzer = CodeAnalyzer()
    project_info = analyzer.analyze_project(str(FIXTURES_DIR))
    chunks = chunk_project(project_info)

    # Generate README
    readme = generator.generate_readme(project_info, chunks)

    assert readme is not None
    assert "Test Project" in readme
    assert "Generated README" in readme


def test_readme_generator_calls_llm():
    """ReadmeGenerator should call LLM during generation."""
    config = Config(ollama_host='http://localhost:11434')
    llm = MockLLMAdapter()
    embedder = MockEmbeddingAdapter()
    vector_store = MockVectorStoreAdapter()

    generator = ReadmeGenerator(llm, embedder, vector_store, config)

    analyzer = CodeAnalyzer()
    project_info = analyzer.analyze_project(str(FIXTURES_DIR))
    chunks = chunk_project(project_info)

    assert llm.call_count == 0

    generator.generate_readme(project_info, chunks)

    assert llm.call_count == 1
    assert llm.last_system_prompt is not None
    assert llm.last_user_prompt is not None


def test_readme_generator_calls_embedder():
    """ReadmeGenerator should call embedder for chunks and queries."""
    config = Config(ollama_host='http://localhost:11434')
    llm = MockLLMAdapter()
    embedder = MockEmbeddingAdapter()
    vector_store = MockVectorStoreAdapter()

    generator = ReadmeGenerator(llm, embedder, vector_store, config)

    analyzer = CodeAnalyzer()
    project_info = analyzer.analyze_project(str(FIXTURES_DIR))
    chunks = chunk_project(project_info)

    assert embedder.call_count == 0

    generator.generate_readme(project_info, chunks)

    # Should embed all chunks + 1 query embedding
    assert embedder.call_count == len(chunks) + 1


def test_readme_generator_uses_vector_store():
    """ReadmeGenerator should store chunks and query vector store."""
    config = Config(ollama_host='http://localhost:11434')
    llm = MockLLMAdapter()
    embedder = MockEmbeddingAdapter()
    vector_store = MockVectorStoreAdapter()

    generator = ReadmeGenerator(llm, embedder, vector_store, config)

    analyzer = CodeAnalyzer()
    project_info = analyzer.analyze_project(str(FIXTURES_DIR))
    chunks = chunk_project(project_info)

    generator.generate_readme(project_info, chunks)

    # Should have created a collection
    assert len(vector_store.collections) > 0

    # Should have stored chunks
    collection_name = list(vector_store.collections.keys())[0]
    collection = vector_store.collections[collection_name]
    assert len(collection['documents']) == len(chunks)


def test_readme_generator_with_empty_project():
    """ReadmeGenerator should handle projects with no files gracefully."""
    config = Config(ollama_host='http://localhost:11434')
    llm = MockLLMAdapter()
    embedder = MockEmbeddingAdapter()
    vector_store = MockVectorStoreAdapter()

    generator = ReadmeGenerator(llm, embedder, vector_store, config)

    # Empty project info
    project_info = {
        'project_name': 'empty_project',
        'file_count': 0,
        'files': [],
        'all_imports': [],
        'total_functions': 0,
        'total_classes': 0
    }
    chunks = []

    # Should not crash
    readme = generator.generate_readme(project_info, chunks)
    assert readme is not None