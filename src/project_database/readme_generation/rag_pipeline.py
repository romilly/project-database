"""RAG pipeline for README generation using hexagonal architecture."""

from typing import Dict, List, Any
from .ports import LLMPort, EmbeddingPort, VectorStorePort
from .config import Config


class ReadmeGenerator:
    """RAG pipeline for README generation using dependency injection."""

    def __init__(
        self,
        llm: LLMPort,
        embedder: EmbeddingPort,
        vector_store: VectorStorePort,
        config: Config
    ):
        """
        Initialize README generator with injected dependencies.

        Args:
            llm: LLM adapter for text generation
            embedder: Embedding adapter for generating vectors
            vector_store: Vector store adapter for chunk storage/retrieval
            config: Configuration object
        """
        self.llm = llm
        self.embedder = embedder
        self.vector_store = vector_store
        self.config = config

    def generate_readme(
        self,
        project_info: Dict[str, Any],
        chunks: List[Dict[str, Any]]
    ) -> str:
        """
        Generate README using RAG pipeline.

        Args:
            project_info: Project metadata from CodeAnalyzer
            chunks: Code chunks from CodeChunker

        Returns:
            Generated README text
        """
        # Handle empty projects
        if len(chunks) == 0:
            return self._generate_empty_project_readme(project_info)

        # 1. Create collection for this project
        collection = self._create_collection(project_info['project_name'])

        # 2. Index chunks with embeddings
        self._index_chunks(collection, chunks)

        # 3. Build project summary
        project_summary = self._build_project_summary(project_info)

        # 4. Retrieve relevant context
        context_chunks = self._retrieve_context(
            collection,
            query="main functionality entry point purpose usage",
            n_results=min(5, len(chunks))
        )

        # 5. Build prompt
        prompt = self._build_readme_prompt(project_summary, context_chunks)

        # 6. Generate with LLM
        readme = self.llm.generate(
            system_prompt='You are a technical documentation expert. Generate clear, concise README files for Python projects.',
            user_prompt=prompt,
            temperature=0.3,
            num_predict=1000
        )

        return readme

    def _create_collection(self, project_name: str):
        """Create or get collection for project."""
        # Sanitize project name for collection
        collection_name = project_name.lower().replace('-', '_').replace('.', '_')[:63]
        return self.vector_store.create_collection(collection_name)

    def _index_chunks(
        self,
        collection: Any,
        chunks: List[Dict[str, Any]]
    ) -> None:
        """Index chunks with embeddings into vector store."""
        documents = []
        metadatas = []
        ids = []
        embeddings = []

        for i, chunk in enumerate(chunks):
            documents.append(chunk['content'])

            # Flatten metadata
            meta = {
                'chunk_type': chunk['type'],
                'filepath': chunk['filepath'],
                'name': chunk.get('name', 'module')
            }
            metadatas.append(meta)
            ids.append(f"chunk_{i}")

            # Generate embedding
            embedding = self.embedder.embed(chunk['content'])
            embeddings.append(embedding)

        # Add to vector store
        self.vector_store.add_chunks(
            collection=collection,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

    def _retrieve_context(
        self,
        collection: Any,
        query: str,
        n_results: int
    ) -> List[str]:
        """Retrieve relevant code chunks."""
        # Generate query embedding
        query_embedding = self.embedder.embed(query)

        # Query vector store
        results = self.vector_store.query(
            collection=collection,
            query_embedding=query_embedding,
            n_results=n_results
        )

        return results

    def _build_project_summary(self, project_info: Dict[str, Any]) -> str:
        """Build high-level project summary."""
        summary = f"Project: {project_info['project_name']}\n"
        summary += f"Files: {project_info['file_count']}\n"
        summary += f"Functions: {project_info['total_functions']}\n"
        summary += f"Classes: {project_info['total_classes']}\n"

        if project_info['all_imports']:
            key_imports = [imp for imp in project_info['all_imports']
                          if not imp.startswith('_') and '.' not in imp][:10]
            if key_imports:
                summary += f"Key dependencies: {', '.join(key_imports)}\n"

        return summary

    def _build_readme_prompt(self, summary: str, context_chunks: List[str]) -> str:
        """Build prompt for README generation."""
        prompt = f"""Based on the following Python project information, generate a README.md file.

PROJECT SUMMARY:
{summary}

KEY CODE COMPONENTS:
{chr(10).join([f"--- Component {i+1} ---" + chr(10) + chunk for i, chunk in enumerate(context_chunks)])}

Generate a README with these sections:
1. Project title and brief description (1-2 sentences)
2. Purpose - What problem does this solve?
3. Features - Key capabilities (bullet points)
4. Installation - How to set it up
5. Usage - Basic usage example with code
6. Requirements - Main dependencies

Keep it concise and practical. Focus on what users need to know to understand and use the project.
"""
        return prompt

    def _generate_empty_project_readme(self, project_info: Dict[str, Any]) -> str:
        """Generate simple README for empty projects."""
        return f"""# {project_info['project_name']}

This project currently has no Python files.

## Getting Started

Add Python files to this project to get started.
"""