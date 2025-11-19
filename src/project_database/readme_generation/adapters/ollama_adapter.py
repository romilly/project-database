"""Ollama adapters for LLM and embeddings."""

import ollama
from typing import List
from ..ports import LLMPort, EmbeddingPort
from ..config import Config


class OllamaLLMAdapter(LLMPort):
    """Adapter for Ollama LLM text generation."""

    def __init__(self, config: Config):
        """
        Initialize Ollama LLM adapter.

        Args:
            config: Configuration with ollama_host and llm_model
        """
        self.client = ollama.Client(host=config.ollama_host)
        self.model = config.llm_model

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        **options
    ) -> str:
        """
        Generate text using Ollama.

        Args:
            system_prompt: System/role instruction
            user_prompt: User's prompt/question
            **options: Ollama options (temperature, num_predict, etc.)

        Returns:
            Generated text
        """
        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    'role': 'system',
                    'content': system_prompt
                },
                {
                    'role': 'user',
                    'content': user_prompt
                }
            ],
            options=options
        )

        return response['message']['content']


class OllamaEmbeddingAdapter(EmbeddingPort):
    """Adapter for Ollama embedding generation."""

    def __init__(self, config: Config):
        """
        Initialize Ollama embedding adapter.

        Args:
            config: Configuration with ollama_host and embed_model
        """
        self.client = ollama.Client(host=config.ollama_host)
        self.model = config.embed_model

    def embed(self, text: str) -> List[float]:
        """
        Generate embedding vector using Ollama.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        response = self.client.embeddings(
            model=self.model,
            prompt=text
        )

        return response['embedding']