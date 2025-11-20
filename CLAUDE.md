# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**project-database** - A Python meta-project to create and maintain a database of projects using SQLAlchemy + SQLite, plus automated README generation using AI. The goal is to track project locations, GitHub sync status, and make it easier to find relevant projects. Built following strict TDD principles and hexagonal architecture where appropriate.

## Project Structure

```
project-database/
├── src/project_database/    # Main source code
├── tests/                    # Test files
│   ├── data/                # Test data files
│   └── output/              # Test output files
├── notebooks/               # Jupyter notebooks for experimentation
├── plan/                    # Planning documents
└── examples/                # Example scripts
```

## Development Approach

**Strict Test-Driven Development (TDD)** - All development follows the Red-Green-Refactor cycle:

1. **Red**: Write a failing test for new functionality
2. **Green**: Write minimal code to make the test pass
3. **Commit**: Commit the passing test and implementation
4. **Refactor** (if needed): Improve test or code while keeping tests green
5. **Retest**: Ensure all tests still pass after refactoring
6. **Commit**: Commit the refactored code
7. **Repeat**: Go back to step 4 for further refactoring or step 1 for next feature

### TDD Workflow Commands

```bash
# Install package in editable mode (required for development)
pip install -e .

# Install with test dependencies
pip install -e .[test]

# TDD Cycle Commands
# 1. Write test, verify it fails
pytest tests/test_new_feature.py::test_specific_function -v

# 2. Run specific test during development
pytest tests/test_new_feature.py::test_specific_function -v

# 3. Run all tests to ensure no regressions
pytest

# 4. Commit after each passing test
git add . && git commit -m "Add feature X with passing test"

# Other useful test commands
pytest -v
pytest -k "test_name_pattern" -v
```

### TDD Guidelines

- **Write the simplest test that can fail first**
- **Write only enough code to make the test pass**
- **Refactor after each green test while keeping all tests passing**
- **Commit after every successful test cycle**
- **One test per commit** - keeps git history clean and focused
- **Test file naming**: `test_[feature_name].py`
- **Test method naming**: `test_[specific_behavior]`

## Testing Structure

Test data in `tests/data/`, output in `tests/output/`.

## Setup and Installation

```bash
# Clone and navigate to project
cd /home/romilly/git/active/project-database

# Create/activate virtual environment (if needed)
python -m venv venv
source venv/bin/activate

# Install in editable mode with test dependencies
pip install -e .[test]

# Verify installation
pytest
```

## Key Dependencies

- **pytest** (>=7.0.0) - Testing framework
- **pytest-cov** - Code coverage reporting
- **notebook** - Jupyter notebook support (dev dependency)

## Development Workflow

### Working with Jupyter Notebooks

**IMPORTANT:** When editing Jupyter notebooks using NotebookEdit tool:
1. The `edit_mode="insert"` parameter inserts cells in **reverse order**
2. After making edits, **ALWAYS verify the cell order** by reading the notebook
3. If cells are out of order, rewrite the entire notebook using the Write tool to ensure correct order
4. Cell order should be logical (headers → code → results → summary)

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_filename.py

# Run specific test function
pytest tests/test_filename.py::test_function_name -v

# Run tests matching a pattern
pytest -k "test_pattern" -v

# Run with coverage report
pytest --cov=project_database --cov-report=html
```

### Git Workflow

After all tests pass, check with user before committing (per global CLAUDE.md instructions).

## Hexagonal Architecture (Ports and Adapters)

### When to Use Hexagonal Architecture

Use hexagonal architecture for components that:
1. **Have external dependencies** - APIs, databases, LLMs, file systems
2. **Need to be testable** - You want fast unit tests without external dependencies
3. **May change implementations** - Different LLM providers, storage backends, etc.
4. **Have clear boundaries** - Distinct business logic vs. infrastructure concerns

**Example in this project:** The `readme_generation` package uses hexagonal architecture because it depends on Ollama (external LLM) and ChromaDB (external vector store).

### Core Concepts

#### Ports (Interfaces)
- Define contracts using Abstract Base Classes (ABC)
- Live in `ports.py`
- No implementation, only method signatures
- Example:
  ```python
  from abc import ABC, abstractmethod

  class LLMPort(ABC):
      @abstractmethod
      def generate(self, system_prompt: str, user_prompt: str, **options) -> str:
          """Generate text using the LLM."""
          pass
  ```

#### Adapters (Implementations)
- Implement the port interfaces
- Live in `adapters/` directory
- Two types:
  1. **Production adapters** - Real implementations (e.g., `OllamaLLMAdapter`)
  2. **Mock adapters** - Testing implementations (e.g., `MockLLMAdapter`)

#### Core Business Logic
- Depends on **ports**, not concrete implementations
- Uses **dependency injection** - adapters passed in via constructor
- Example:
  ```python
  class ReadmeGenerator:
      def __init__(self, llm: LLMPort, embedder: EmbeddingPort,
                   vector_store: VectorStorePort, config: Config):
          self.llm = llm  # Any implementation of LLMPort works!
          # ...
  ```

### TDD with Hexagonal Architecture

**Recommended workflow:**

1. **Write integration test first** (defines expected behavior with real adapters)
   - Mark with `@pytest.mark.integration`
   - Will fail initially (RED)

2. **Define ports** (ABC interfaces)
   - What methods do we need?
   - What parameters and return types?

3. **Create mock adapters** (for testing)
   - Implement ports with simple, deterministic behavior
   - Test the mock adapters work

4. **Implement core logic with unit tests**
   - Use mock adapters for fast, isolated tests
   - Test business logic without external dependencies
   - Make tests pass (GREEN)

5. **Implement production adapters**
   - Implement ports with real external services
   - Make integration test pass (GREEN)

### Benefits

1. **Testability**
   - Unit tests use mocks (fast, no external deps, ~3 seconds)
   - Integration tests use real adapters (slow, requires setup, ~15 seconds)
   - Can run unit tests in CI/CD without external services

2. **Flexibility**
   - Easy to swap implementations (different LLM providers, databases, etc.)
   - No changes to core logic required
   - Just implement the port interface

3. **Separation of Concerns**
   - Business logic isolated from infrastructure
   - Clear boundaries between layers
   - Easy to understand and maintain

4. **Development Speed**
   - Fast unit tests enable rapid TDD cycles
   - Don't wait for external services during development
   - Integration tests verify real adapters work

### Example Structure

```
src/project_database/your_feature/
├── __init__.py                 # Public API
├── ports.py                    # Port interfaces (ABC)
├── core_logic.py              # Business logic (depends on ports)
└── adapters/
    ├── __init__.py
    ├── mock_adapters.py       # Mock implementations for testing
    └── real_adapter.py        # Production implementation

tests/your_feature/
├── test_mock_adapters.py      # Test mocks implement ports correctly
├── test_core_logic.py         # Unit tests with mocks
└── test_integration.py        # Integration tests with real adapters
```

### Testing Strategy

```bash
# Fast unit tests only (use mocks, no external deps)
pytest -m "not integration"

# All tests including integration (requires external services)
pytest

# Just integration tests
pytest -m integration
```

### Key Guidelines

1. **Always define ports first** - Think about the interface before implementation
2. **Mock adapters should be simple** - Just enough to test core logic
3. **One port per external dependency** - LLM, database, file system, etc.
4. **Inject dependencies** - Don't create adapters inside core logic
5. **Test mocks test the interface** - Verify mocks implement ports correctly
6. **Integration tests verify real adapters** - Test with actual external services
7. **Keep it simple** - Don't over-architect; use only when benefits are clear

### When NOT to Use Hexagonal Architecture

Don't use hexagonal architecture for:
- Simple utilities with no external dependencies
- One-off scripts
- Code that will never change implementations
- When the overhead isn't worth the benefits

**Rule of thumb:** If you can't imagine swapping the implementation or it has no external dependencies, keep it simple.

## README Generation Package

The `src/project_database/readme_generation/` package demonstrates hexagonal architecture:

- **Ports:** `LLMPort`, `EmbeddingPort`, `VectorStorePort`
- **Production Adapters:** `OllamaLLMAdapter`, `OllamaEmbeddingAdapter`, `ChromaDBAdapter`
- **Mock Adapters:** `MockLLMAdapter`, `MockEmbeddingAdapter`, `MockVectorStoreAdapter`
- **Core Logic:** `ReadmeGenerator` (depends only on ports)
- **Tests:** 37 unit tests (with mocks) + 4 integration tests (with real adapters)

See the code for a complete working example.