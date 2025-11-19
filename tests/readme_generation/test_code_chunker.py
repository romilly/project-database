"""Tests for code chunker."""

from pathlib import Path
from project_database.readme_generation.ast_analyzer import CodeAnalyzer
from project_database.readme_generation.code_chunker import CodeChunker, chunk_project


# Test fixtures path
FIXTURES_DIR = Path(__file__).parent / 'fixtures'
SAMPLE_MODULE = FIXTURES_DIR / 'sample_module.py'


def test_chunk_file_creates_module_chunk():
    """Should create a module-level chunk with docstring and imports."""
    analyzer = CodeAnalyzer()
    file_info = analyzer.analyze_file(str(SAMPLE_MODULE))

    chunker = CodeChunker()
    chunks = chunker.chunk_file(file_info)

    # Should have at least one module chunk
    module_chunks = [c for c in chunks if c['type'] == 'module']
    assert len(module_chunks) == 1

    module_chunk = module_chunks[0]
    assert 'Sample module' in module_chunk['content']
    assert module_chunk['filepath'] == str(SAMPLE_MODULE)


def test_chunk_file_creates_function_chunks():
    """Should create chunks for each function."""
    analyzer = CodeAnalyzer()
    file_info = analyzer.analyze_file(str(SAMPLE_MODULE))

    chunker = CodeChunker()
    chunks = chunker.chunk_file(file_info)

    # Should have function chunks (including methods)
    function_chunks = [c for c in chunks if c['type'] == 'function']
    assert len(function_chunks) == 5  # 2 functions + 3 methods

    # Check one function chunk in detail
    simple_func_chunks = [c for c in function_chunks if c['name'] == 'simple_function']
    assert len(simple_func_chunks) == 1

    func_chunk = simple_func_chunks[0]
    assert 'def simple_function' in func_chunk['content']
    assert func_chunk['metadata']['type'] == 'function'
    assert func_chunk['metadata']['name'] == 'simple_function'
    assert func_chunk['metadata']['args'] == ['arg1', 'arg2']


def test_chunk_file_creates_class_chunks():
    """Should create chunks for each class."""
    analyzer = CodeAnalyzer()
    file_info = analyzer.analyze_file(str(SAMPLE_MODULE))

    chunker = CodeChunker()
    chunks = chunker.chunk_file(file_info)

    # Should have class chunks
    class_chunks = [c for c in chunks if c['type'] == 'class']
    assert len(class_chunks) == 2

    # Check one class chunk in detail
    sample_class_chunks = [c for c in class_chunks if c['name'] == 'SampleClass']
    assert len(sample_class_chunks) == 1

    class_chunk = sample_class_chunks[0]
    assert 'class SampleClass' in class_chunk['content']
    assert class_chunk['metadata']['type'] == 'class'
    assert class_chunk['metadata']['name'] == 'SampleClass'
    assert 'method_one' in class_chunk['metadata']['methods']


def test_chunk_file_includes_metadata():
    """Should include appropriate metadata in each chunk."""
    analyzer = CodeAnalyzer()
    file_info = analyzer.analyze_file(str(SAMPLE_MODULE))

    chunker = CodeChunker()
    chunks = chunker.chunk_file(file_info)

    for chunk in chunks:
        assert 'type' in chunk
        assert 'filepath' in chunk
        assert 'content' in chunk
        assert 'metadata' in chunk


def test_chunk_project_processes_all_files():
    """Should chunk all files in a project."""
    analyzer = CodeAnalyzer()
    project_info = analyzer.analyze_project(str(FIXTURES_DIR))

    all_chunks = chunk_project(project_info)

    # Should have chunks from the sample module
    assert len(all_chunks) > 0

    # Should have different types of chunks
    chunk_types = set(c['type'] for c in all_chunks)
    assert 'module' in chunk_types
    assert 'function' in chunk_types
    assert 'class' in chunk_types


def test_chunk_project_returns_list():
    """Should return a list of chunk dictionaries."""
    analyzer = CodeAnalyzer()
    project_info = analyzer.analyze_project(str(FIXTURES_DIR))

    all_chunks = chunk_project(project_info)

    assert isinstance(all_chunks, list)
    assert all(isinstance(chunk, dict) for chunk in all_chunks)