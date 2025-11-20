# project-database

A Python meta-project to create and maintain a database of my projects, plus automated README generation using AI.

## Features

### Project Database
Track and manage your projects with SQLAlchemy + SQLite:
- **Fast scanning** - Scans 300+ projects in 1.3 seconds (parallel processing)
- **Metadata extraction** - Automatically finds README, Logseq pages, GitHub URLs
- **Timestamp tracking** - Monitors created_at, updated_at, last_file_modified
- **Smart filtering** - Find projects without READMEs, by activity, etc.
- **GitHub integration** - Extracts repository URLs from git remotes

### README Generation
Automatically generate README files for Python projects using:
- **AST-aware code analysis** - Understands your code structure
- **RAG (Retrieval-Augmented Generation)** - Retrieves relevant context
- **Local LLMs via Ollama** - Zero API costs, runs on your hardware
- **Hexagonal architecture** - Clean, testable, swappable components

**Quality Evaluation (5 projects × 3 models):**
- **qwen2.5-coder:32b** - Best quality (4.2/5 accuracy, 4.6/5 clarity) - Recommended
- **qwen2.5-coder:14b** - Balanced (4.0/5 accuracy, 4.0/5 clarity)
- **qwen2.5-coder:7b** - Fast (3.6/5 accuracy, 3.8/5 clarity)

**Architecture:**
- Ports & Adapters pattern for flexibility
- Mock adapters for fast testing (41 tests, 100% passing)
- Remote Ollama support (no local GPU required)
- Easy to swap LLM providers

## Installation

### Basic Installation
```bash
pip install -e .
```

### Development Installation
```bash
pip install -e .[test]
pytest
```

### README Generation Setup
1. Install Ollama and required models (on local or remote machine)
2. Configure `.env` with Ollama host:
   ```bash
   OLLAMA_HOST=http://your-ollama-host:11434
   ```
3. Install additional dependencies:
   ```bash
   pip install ollama chromadb
   ```

## Usage

### Generate README for a Project
```python
from project_database.readme_generation import generate_readme_for_project

# Simple usage (reads OLLAMA_HOST from .env)
readme = generate_readme_for_project('/path/to/your/project')

# Custom configuration
readme = generate_readme_for_project(
    '/path/to/your/project',
    llm_model='qwen2.5-coder:32b',  # Recommended for best quality
    output_path='/path/to/output/README.md'
)
```

### Advanced Usage with Custom Adapters
```python
from project_database.readme_generation import (
    Config, ReadmeGenerator, CodeAnalyzer, chunk_project
)
from project_database.readme_generation.adapters.ollama_adapter import (
    OllamaLLMAdapter, OllamaEmbeddingAdapter
)
from project_database.readme_generation.adapters.chromadb_adapter import (
    ChromaDBAdapter
)

# Configure
config = Config(
    ollama_host='http://polwarth:11434',
    llm_model='qwen2.5-coder:7b',
    embed_model='nomic-embed-text'
)

# Create adapters (or use your own implementations!)
llm = OllamaLLMAdapter(config)
embedder = OllamaEmbeddingAdapter(config)
vector_store = ChromaDBAdapter(config)

# Generate README
generator = ReadmeGenerator(llm, embedder, vector_store, config)
analyzer = CodeAnalyzer()
project_info = analyzer.analyze_project('/path/to/project')
chunks = chunk_project(project_info)
readme = generator.generate_readme(project_info, chunks)
```

## Testing

### Run All Tests
```bash
pytest
```

### Run Only Unit Tests (fast, no external dependencies)
```bash
pytest -m "not integration"
```

### Run Integration Tests (requires Ollama)
```bash
pytest -m integration
```

## Architecture

The README generation system uses **Hexagonal Architecture** (Ports & Adapters):

- **Ports** - Interfaces defining contracts (LLMPort, EmbeddingPort, VectorStorePort)
- **Production Adapters** - Real implementations (Ollama, ChromaDB)
- **Mock Adapters** - Fast testing without external dependencies
- **Core Logic** - Business logic depends only on ports, not implementations

**Benefits:**
- ✅ Testable without LLM running (37 fast unit tests)
- ✅ Easy to swap LLM providers (OpenAI, Anthropic, etc.)
- ✅ Clean separation of concerns
- ✅ CI/CD friendly

## Model Selection Guide

Based on evaluation of 15 generated READMEs across 5 diverse projects:

| Model | Accuracy | Clarity | Speed | Best For |
|-------|----------|---------|-------|----------|
| **32b** | 4.2/5 | 4.6/5 | ~45s | Production, customer-facing docs |
| **14b** | 4.0/5 | 4.0/5 | ~25s | Balanced quality/speed |
| **7b** | 3.6/5 | 3.8/5 | ~12s | Quick drafts, simple projects |

**Recommendation:** Use **32b for production** - best quality and structure, worth the extra time.

**Note:** All models require manual review for:
- Technical accuracy of algorithms
- Verification of import paths
- Testing usage examples

## Development

Built with strict Test-Driven Development (TDD):
- 41 passing tests (37 unit + 4 integration)
- Red-Green-Refactor cycle for all features
- Commit after each passing test
- 100% test coverage on core modules

### Project Status
- ✅ **Database system** - 25 tests, scans 321 projects in 1.3s
- ✅ **README generation** - 41 tests, hexagonal architecture
- ✅ **Quality evaluation** - 15 READMEs tested, models ranked
- 🚀 **Ready for batch processing** - 164 projects missing READMEs

## Credits

Built with help from Claude Code using hexagonal architecture and strict TDD.