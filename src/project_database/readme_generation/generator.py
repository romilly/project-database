"""Convenience functions for README generation."""

import os
from pathlib import Path
from dotenv import load_dotenv

from .config import Config
from .ast_analyzer import CodeAnalyzer
from .code_chunker import chunk_project
from .rag_pipeline import ReadmeGenerator
from .adapters.ollama_adapter import OllamaLLMAdapter, OllamaEmbeddingAdapter
from .adapters.chromadb_adapter import ChromaDBAdapter


def generate_readme_for_project(
    project_path: str,
    output_path: str = None,
    ollama_host: str = None,
    llm_model: str = 'qwen2.5-coder:7b',
    embed_model: str = 'nomic-embed-text',
    db_path: str = './chroma_db'
) -> str:
    """
    Generate README for a project using the complete RAG pipeline.

    This is a convenience function that:
    1. Loads configuration from .env (if not provided)
    2. Analyzes the project code
    3. Chunks the code
    4. Creates adapters
    5. Generates README using RAG
    6. Optionally saves to file

    Args:
        project_path: Path to project directory
        output_path: Where to save README (default: project_path/README_GENERATED.md)
        ollama_host: Ollama server URL (default: from OLLAMA_HOST env var)
        llm_model: LLM model to use
        embed_model: Embedding model to use
        db_path: ChromaDB storage path

    Returns:
        Generated README text

    Raises:
        ValueError: If ollama_host not provided and OLLAMA_HOST not in env

    Example:
        >>> readme = generate_readme_for_project('/path/to/project')
        >>> print(readme)
    """
    # Load environment variables
    load_dotenv()

    # Get Ollama host from env if not provided
    if ollama_host is None:
        ollama_host = os.getenv('OLLAMA_HOST')
        if not ollama_host:
            raise ValueError(
                "ollama_host not provided and OLLAMA_HOST not set in .env file. "
                "Either pass ollama_host parameter or set OLLAMA_HOST in .env"
            )

    # 1. Create configuration
    config = Config(
        ollama_host=ollama_host,
        llm_model=llm_model,
        embed_model=embed_model,
        db_path=db_path
    )

    # 2. Analyze project
    print(f"\n{'='*60}")
    print(f"Analyzing {project_path}")
    print('='*60)

    analyzer = CodeAnalyzer()
    project_info = analyzer.analyze_project(project_path)

    if project_info['file_count'] == 0:
        print("No Python files found!")
        return None

    print(f"✓ Found {project_info['file_count']} Python files")
    print(f"  - {project_info['total_functions']} functions")
    print(f"  - {project_info['total_classes']} classes")

    # 3. Chunk code
    print(f"\nChunking code...")
    chunks = chunk_project(project_info)
    print(f"✓ Created {len(chunks)} chunks")

    # 4. Create adapters
    print(f"\nInitializing RAG pipeline...")
    llm = OllamaLLMAdapter(config)
    embedder = OllamaEmbeddingAdapter(config)
    vector_store = ChromaDBAdapter(config)

    # 5. Generate README
    print(f"Generating README...")
    generator = ReadmeGenerator(llm, embedder, vector_store, config)
    readme = generator.generate_readme(project_info, chunks)

    # 6. Save README
    if output_path is None:
        output_path = Path(project_path) / "README_GENERATED.md"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(readme)

    print(f"\n{'='*60}")
    print(f"✓ README generated: {output_path}")
    print('='*60)

    return readme