"""
README generation package using AST-aware RAG with local LLMs.

This package provides tools to automatically generate README.md files
for Python projects by analyzing code structure and using RAG with
local Ollama models.
"""

from .config import Config
from .ast_analyzer import CodeAnalyzer
from .code_chunker import CodeChunker, chunk_project
from .rag_pipeline import ReadmeGenerator
from .generator import generate_readme_for_project

__all__ = [
    'Config',
    'CodeAnalyzer',
    'CodeChunker',
    'chunk_project',
    'ReadmeGenerator',
    'generate_readme_for_project',
]