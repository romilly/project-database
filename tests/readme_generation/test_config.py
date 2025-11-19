"""Tests for configuration."""

from project_database.readme_generation.config import Config


def test_config_requires_ollama_host():
    """Config should require ollama_host parameter."""
    config = Config(ollama_host='http://localhost:11434')
    assert config.ollama_host == 'http://localhost:11434'


def test_config_has_default_llm_model():
    """Config should have a default LLM model."""
    config = Config(ollama_host='http://localhost:11434')
    assert config.llm_model == 'qwen2.5-coder:7b'


def test_config_has_default_embed_model():
    """Config should have a default embedding model."""
    config = Config(ollama_host='http://localhost:11434')
    assert config.embed_model == 'nomic-embed-text'


def test_config_has_default_db_path():
    """Config should have a default ChromaDB path."""
    config = Config(ollama_host='http://localhost:11434')
    assert config.db_path == './chroma_db'


def test_config_can_be_customized():
    """Config should accept custom values."""
    custom_config = Config(
        ollama_host='http://custom:11434',
        llm_model='custom-model:7b',
        embed_model='custom-embed',
        db_path='/custom/path'
    )

    assert custom_config.ollama_host == 'http://custom:11434'
    assert custom_config.llm_model == 'custom-model:7b'
    assert custom_config.embed_model == 'custom-embed'
    assert custom_config.db_path == '/custom/path'