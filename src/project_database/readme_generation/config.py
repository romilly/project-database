"""Configuration for README generation."""


class Config:
    """Configuration for README generation using Ollama and ChromaDB."""

    def __init__(
        self,
        ollama_host: str,
        llm_model: str = 'qwen2.5-coder:7b',
        embed_model: str = 'nomic-embed-text',
        db_path: str = './chroma_db'
    ):
        """
        Initialize configuration.

        Args:
            ollama_host: Ollama server URL (required, e.g., 'http://polwarth:11434')
            llm_model: LLM model for generation (default: qwen2.5-coder:7b)
            embed_model: Embedding model (default: nomic-embed-text)
            db_path: ChromaDB storage path (default: ./chroma_db)
        """
        self.ollama_host = ollama_host
        self.llm_model = llm_model
        self.embed_model = embed_model
        self.db_path = db_path