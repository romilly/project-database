# README Generator Implementation Guide
## Simple AST-Aware RAG Pipeline with Local LLMs

**Project Goal**: Build a minimal viable system to automatically generate READMEs for 100+ small Python projects using local LLMs, zero external API costs.

**Your Context**:
- Projects: Small (1 day - 2 weeks effort), single developer
- Hardware: Intel machine with 12GB 3060 GPU, 16GB Jetson Xavier
- Models: Qwen 2.5 Coder 7B/14B via Ollama
- Tolerance: Slow execution OK (can run for days)
- Priority: Zero cost > Speed

---

## Phase 1: Minimal Viable Pipeline (2-3 days)

### System Architecture

```
[Python Projects] 
    ↓
[AST Parser] → Extract structure (functions, classes, imports)
    ↓
[Code Chunker] → Split at function/class boundaries
    ↓
[Embedder] → Convert to vectors (all-MiniLM-L6-v2)
    ↓
[ChromaDB] → Store with metadata
    ↓
[Retriever] → Get top-5 relevant chunks
    ↓
[Qwen 2.5 Coder] → Generate README via Ollama
    ↓
[README.md]
```

### Dependencies

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.com/install.sh | sh

# Pull model
ollama pull qwen2.5-coder:7b

# Python dependencies
pip install chromadb sentence-transformers ollama
```

### Core Components

#### 1. AST-Based Code Analyzer (`ast_analyzer.py`)

```python
import ast
import os
from pathlib import Path
from typing import Dict, List, Any


class CodeAnalyzer:
    """Extract structural information from Python files using AST."""
    
    def analyze_file(self, filepath: str) -> Dict[str, Any]:
        """Parse a single Python file and extract metadata."""
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                source = f.read()
                tree = ast.parse(source)
            except SyntaxError:
                return {'error': 'syntax_error', 'filepath': filepath}
        
        return {
            'filepath': filepath,
            'functions': self._extract_functions(tree),
            'classes': self._extract_classes(tree),
            'imports': self._extract_imports(tree),
            'module_docstring': ast.get_docstring(tree),
            'source': source
        }
    
    def _extract_functions(self, tree: ast.AST) -> List[Dict]:
        """Extract function definitions with signatures."""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    'name': node.name,
                    'args': [arg.arg for arg in node.args.args],
                    'docstring': ast.get_docstring(node),
                    'lineno': node.lineno,
                    'is_async': isinstance(node, ast.AsyncFunctionDef)
                })
        return functions
    
    def _extract_classes(self, tree: ast.AST) -> List[Dict]:
        """Extract class definitions."""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [m for m in node.body if isinstance(m, ast.FunctionDef)]
                classes.append({
                    'name': node.name,
                    'bases': [self._get_name(base) for base in node.bases],
                    'methods': [m.name for m in methods],
                    'docstring': ast.get_docstring(node),
                    'lineno': node.lineno
                })
        return classes
    
    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract import statements."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}" if module else alias.name)
        return imports
    
    def _get_name(self, node: ast.AST) -> str:
        """Extract name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return str(node)
    
    def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """Analyze all Python files in a project."""
        project_path = Path(project_path)
        files = []
        
        for py_file in project_path.rglob('*.py'):
            # Skip common non-project files
            if any(skip in str(py_file) for skip in ['.venv', 'venv', '__pycache__', '.git']):
                continue
            
            file_info = self.analyze_file(str(py_file))
            if 'error' not in file_info:
                files.append(file_info)
        
        return {
            'project_path': str(project_path),
            'project_name': project_path.name,
            'file_count': len(files),
            'files': files,
            'all_imports': list(set(sum([f['imports'] for f in files], []))),
            'total_functions': sum(len(f['functions']) for f in files),
            'total_classes': sum(len(f['classes']) for f in files)
        }
```

#### 2. AST-Aware Code Chunker (`code_chunker.py`)

```python
from typing import List, Dict, Any


class CodeChunker:
    """Chunk code at function/class boundaries for embedding."""
    
    def chunk_file(self, file_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create chunks from analyzed file."""
        chunks = []
        
        # Module-level chunk (imports + module docstring)
        if file_info.get('module_docstring') or file_info.get('imports'):
            chunk = {
                'type': 'module',
                'filepath': file_info['filepath'],
                'content': self._build_module_chunk(file_info),
                'metadata': {
                    'type': 'module',
                    'imports': file_info.get('imports', [])
                }
            }
            chunks.append(chunk)
        
        # Function chunks
        source_lines = file_info['source'].splitlines()
        for func in file_info.get('functions', []):
            chunk = {
                'type': 'function',
                'filepath': file_info['filepath'],
                'name': func['name'],
                'content': self._extract_function_source(source_lines, func),
                'metadata': {
                    'type': 'function',
                    'name': func['name'],
                    'args': func['args'],
                    'docstring': func.get('docstring', '')
                }
            }
            chunks.append(chunk)
        
        # Class chunks
        for cls in file_info.get('classes', []):
            chunk = {
                'type': 'class',
                'filepath': file_info['filepath'],
                'name': cls['name'],
                'content': self._extract_class_source(source_lines, cls),
                'metadata': {
                    'type': 'class',
                    'name': cls['name'],
                    'methods': cls['methods'],
                    'bases': cls['bases'],
                    'docstring': cls.get('docstring', '')
                }
            }
            chunks.append(chunk)
        
        return chunks
    
    def _build_module_chunk(self, file_info: Dict[str, Any]) -> str:
        """Build module-level chunk content."""
        parts = []
        
        if file_info.get('module_docstring'):
            parts.append(f'"""Module: {Path(file_info["filepath"]).name}')
            parts.append(file_info['module_docstring'])
            parts.append('"""')
        
        if file_info.get('imports'):
            parts.append('\n# Imports:')
            parts.extend(file_info['imports'][:10])  # Limit to first 10
        
        return '\n'.join(parts)
    
    def _extract_function_source(self, source_lines: List[str], func: Dict) -> str:
        """Extract function source from original file."""
        # Simple heuristic: take 20 lines from function start
        start = func['lineno'] - 1
        end = min(start + 20, len(source_lines))
        
        lines = source_lines[start:end]
        
        # Add context header
        header = f"# Function: {func['name']}({', '.join(func['args'])})\n"
        return header + '\n'.join(lines)
    
    def _extract_class_source(self, source_lines: List[str], cls: Dict) -> str:
        """Extract class source from original file."""
        # Simple heuristic: take 30 lines from class start
        start = cls['lineno'] - 1
        end = min(start + 30, len(source_lines))
        
        lines = source_lines[start:end]
        
        # Add context header
        header = f"# Class: {cls['name']}"
        if cls['bases']:
            header += f" (inherits from: {', '.join(cls['bases'])})"
        header += f"\n# Methods: {', '.join(cls['methods'])}\n"
        
        return header + '\n'.join(lines)


def chunk_project(project_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Chunk all files in analyzed project."""
    chunker = CodeChunker()
    all_chunks = []
    
    for file_info in project_info['files']:
        chunks = chunker.chunk_file(file_info)
        all_chunks.extend(chunks)
    
    return all_chunks
```

#### 3. RAG Pipeline (`rag_pipeline.py`)

```python
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import ollama
from pathlib import Path
from typing import List, Dict, Any
import json


class ReadmeGenerator:
    """RAG pipeline for README generation."""
    
    def __init__(self, db_path: str = "./chroma_db", model_name: str = "qwen2.5-coder:7b"):
        """Initialize RAG components."""
        # ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        
        # Sentence transformer for embeddings
        print("Loading embedding model...")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Ollama model name
        self.model_name = model_name
        
        print(f"RAG pipeline initialized with {model_name}")
    
    def create_collection(self, project_name: str) -> chromadb.Collection:
        """Create or get collection for project."""
        # Use project name as collection name (sanitized)
        collection_name = project_name.lower().replace('-', '_').replace('.', '_')[:63]
        
        # Delete existing collection if it exists
        try:
            self.chroma_client.delete_collection(collection_name)
        except:
            pass
        
        collection = self.chroma_client.create_collection(
            name=collection_name,
            metadata={"description": f"Code chunks for {project_name}"}
        )
        
        return collection
    
    def index_project(self, project_info: Dict[str, Any], chunks: List[Dict[str, Any]]) -> chromadb.Collection:
        """Index project chunks into ChromaDB."""
        collection = self.create_collection(project_info['project_name'])
        
        print(f"Indexing {len(chunks)} chunks...")
        
        # Prepare data for batch insertion
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            documents.append(chunk['content'])
            
            # Flatten metadata for ChromaDB
            meta = {
                'chunk_type': chunk['type'],
                'filepath': chunk['filepath'],
                'name': chunk.get('name', 'module')
            }
            metadatas.append(meta)
            
            ids.append(f"chunk_{i}")
        
        # Generate embeddings
        print("Generating embeddings...")
        embeddings = self.embedder.encode(documents, show_progress_bar=True)
        
        # Add to collection
        collection.add(
            documents=documents,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"Indexed {len(chunks)} chunks into ChromaDB")
        return collection
    
    def retrieve_context(self, collection: chromadb.Collection, query: str, n_results: int = 5) -> List[str]:
        """Retrieve relevant code chunks."""
        # Generate query embedding
        query_embedding = self.embedder.encode([query])[0]
        
        # Query ChromaDB
        results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results
        )
        
        return results['documents'][0]
    
    def generate_readme(self, project_info: Dict[str, Any], collection: chromadb.Collection) -> str:
        """Generate README using RAG."""
        
        # Build project summary
        project_summary = self._build_project_summary(project_info)
        
        # Retrieve relevant context
        context_chunks = self.retrieve_context(
            collection,
            query="main functionality entry point purpose usage",
            n_results=5
        )
        
        # Build prompt
        prompt = self._build_readme_prompt(project_summary, context_chunks)
        
        # Generate with Ollama
        print("Generating README with Ollama...")
        response = ollama.chat(
            model=self.model_name,
            messages=[
                {
                    'role': 'system',
                    'content': 'You are a technical documentation expert. Generate clear, concise README files for Python projects.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            options={
                'temperature': 0.3,  # Lower temperature for more focused output
                'num_predict': 1000  # Limit length
            }
        )
        
        return response['message']['content']
    
    def _build_project_summary(self, project_info: Dict[str, Any]) -> str:
        """Build high-level project summary."""
        summary = f"Project: {project_info['project_name']}\n"
        summary += f"Files: {project_info['file_count']}\n"
        summary += f"Functions: {project_info['total_functions']}\n"
        summary += f"Classes: {project_info['total_classes']}\n"
        
        if project_info['all_imports']:
            key_imports = [imp for imp in project_info['all_imports'] 
                          if not imp.startswith('_') and '.' not in imp][:10]
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


def generate_readme_for_project(project_path: str, output_path: str = None):
    """Complete pipeline: analyze -> chunk -> index -> generate."""
    from ast_analyzer import CodeAnalyzer
    from code_chunker import chunk_project
    
    # 1. Analyze project
    print(f"\n=== Analyzing {project_path} ===")
    analyzer = CodeAnalyzer()
    project_info = analyzer.analyze_project(project_path)
    
    if project_info['file_count'] == 0:
        print("No Python files found!")
        return
    
    print(f"Found {project_info['file_count']} Python files")
    
    # 2. Chunk code
    print("\n=== Chunking code ===")
    chunks = chunk_project(project_info)
    print(f"Created {len(chunks)} chunks")
    
    # 3. Index and generate
    print("\n=== Indexing and generating README ===")
    generator = ReadmeGenerator()
    collection = generator.index_project(project_info, chunks)
    readme = generator.generate_readme(project_info, collection)
    
    # 4. Save README
    if output_path is None:
        output_path = Path(project_path) / "README.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(readme)
    
    print(f"\n✓ README generated: {output_path}")
    return readme


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python rag_pipeline.py <project_path>")
        sys.exit(1)
    
    project_path = sys.argv[1]
    generate_readme_for_project(project_path)
```

---

## Usage

### Single Project

```bash
# Analyze and generate README for one project
python rag_pipeline.py /path/to/your/project
```

### Batch Processing (Jupyter Notebook)

```python
# batch_process.ipynb

from pathlib import Path
from rag_pipeline import generate_readme_for_project
import time

# List of project directories
projects = [
    "/path/to/project1",
    "/path/to/project2",
    # ... add all 100+ projects
]

# Or auto-discover projects
projects_root = Path("/path/to/all/projects")
projects = [str(p) for p in projects_root.iterdir() if p.is_dir() and not p.name.startswith('.')]

results = []

for i, project_path in enumerate(projects):
    print(f"\n{'='*60}")
    print(f"Processing {i+1}/{len(projects)}: {Path(project_path).name}")
    print('='*60)
    
    try:
        start = time.time()
        readme = generate_readme_for_project(project_path)
        elapsed = time.time() - start
        
        results.append({
            'project': Path(project_path).name,
            'status': 'success',
            'time': elapsed
        })
        
        print(f"✓ Success in {elapsed:.1f}s")
        
    except Exception as e:
        results.append({
            'project': Path(project_path).name,
            'status': 'error',
            'error': str(e)
        })
        print(f"✗ Error: {e}")

# Summary
print("\n" + "="*60)
print("BATCH PROCESSING SUMMARY")
print("="*60)
successes = sum(1 for r in results if r['status'] == 'success')
print(f"Successful: {successes}/{len(projects)}")
print(f"Average time: {sum(r.get('time', 0) for r in results)/successes:.1f}s")

# Save results
import json
with open('batch_results.json', 'w') as f:
    json.dump(results, f, indent=2)
```

---

## Optimization Tips

### 1. Model Selection for Your Hardware

**12GB 3060 GPU** (recommended for speed):
```bash
# Fastest on GPU
ollama pull qwen2.5-coder:7b       # ~4.7GB, good quality

# Better quality, still fits
ollama pull qwen2.5-coder:14b      # ~8.8GB, excellent quality
```

**16GB Jetson Xavier** (if you want to free up your workstation):
```bash
# Jetson works best with 7B models
ollama pull qwen2.5-coder:7b

# Or try smaller for faster inference
ollama pull qwen2.5-coder:3b       # ~2GB, adequate for small projects
```

### 2. Speed vs Quality Trade-offs

For **100+ projects**, you likely want consistency over perfection:

```python
# In generate_readme method, adjust Ollama options:

options={
    'temperature': 0.2,      # Lower = more deterministic (0.2-0.4 recommended)
    'num_predict': 800,      # Shorter READMEs = faster (800-1200)
    'top_p': 0.9,           # Nucleus sampling for quality
    'repeat_penalty': 1.1    # Avoid repetition
}
```

### 3. Caching for Repeated Runs

ChromaDB is persistent, so re-running on the same project reuses embeddings:

```python
# Check if collection exists before re-indexing
try:
    collection = self.chroma_client.get_collection(collection_name)
    print("Using cached collection")
    return collection
except:
    # Create new collection
    return self.create_collection(project_name)
```

### 4. Batch Efficiency

Process multiple projects in one session to keep model loaded:

```python
# Load model once
generator = ReadmeGenerator()  # Model stays in memory

for project in projects:
    # Each project reuses loaded model
    readme = generate_readme_for_project(project)
```

Expected performance on 12GB 3060:
- **Qwen 2.5 Coder 7B**: 30-60 seconds per project
- **Qwen 2.5 Coder 14B**: 60-90 seconds per project
- **100 projects**: 1-2 hours total (can run overnight)

---

## Validation & Iteration

### Quick Quality Check

After generating 5-10 READMEs, manually review:

```python
# quality_check.py
import random
from pathlib import Path

# Sample random projects
projects_with_readmes = list(Path("/path/to/projects").glob("*/README.md"))
sample = random.sample(projects_with_readmes, min(10, len(projects_with_readmes)))

for readme_path in sample:
    print(f"\n{'='*60}")
    print(f"Project: {readme_path.parent.name}")
    print('='*60)
    print(open(readme_path).read())
    print("\nPress Enter for next, 'q' to quit...")
    if input().strip() == 'q':
        break
```

**Look for**:
- Hallucinations (mentions non-existent features)
- Missing key functionality
- Format issues
- Too verbose or too terse

### Common Fixes

**Problem: Too generic**
→ Increase `n_results` from 5 to 8-10 for more context

**Problem: Hallucinations**
→ Lower temperature to 0.1-0.2
→ Add more AST metadata to chunks

**Problem: Missing features**
→ Improve retrieval query: add more keywords relevant to your projects

**Problem: Inconsistent format**
→ Make prompt more structured with explicit headings

---

## Cost Tracking (Spoiler: $0)

Since everything runs locally:
- Model inference: **$0** (local GPU)
- Embeddings: **$0** (local CPU/GPU)
- Storage: **~50-100MB** per 100 projects in ChromaDB
- Electricity: **~$0.50-1.00** per 100 projects (rough estimate)

Compare to API approach:
- Claude API: ~$3-5 per README × 100 = **$300-500**
- GPT-4: ~$2-4 per README × 100 = **$200-400**

**Your approach saves $200-500** while giving you full control and privacy.

---

## Next Steps After MVP

Once the basic pipeline works, consider:

1. **Function calling for structured output**
   - Define JSON schema for README sections
   - Use Qwen's native tool support via Ollama

2. **AST dependency ordering**
   - Process main entry points first
   - Build better context from call graphs

3. **Multi-agent refinement**
   - First pass: generate content
   - Second pass: verify and improve

4. **Custom templates**
   - Define README templates per project type
   - Inject your preferred style/sections

But start simple. Get the MVP working first, then iterate based on actual results.

---

## Troubleshooting

**"CUDA out of memory"**
→ Use 7B model instead of 14B
→ Close other GPU applications
→ Reduce `num_predict` to 600-800

**"Model generates garbage"**
→ Check temperature isn't too high (keep ≤0.4)
→ Verify model pulled correctly: `ollama list`
→ Try regenerating with different random seed

**"ChromaDB errors"**
→ Delete `./chroma_db` directory and re-run
→ Check disk space (needs ~1GB free)

**"Too slow"**
→ Use 3B or 7B model
→ Reduce `n_results` from 5 to 3
→ Limit `num_predict` to 600

---

## Summary

This pipeline gives you:
- ✓ Zero API costs (100% local)
- ✓ AST-aware chunking (respects code structure)
- ✓ Semantic retrieval (finds relevant context)
- ✓ Batch processing (can handle 100+ projects)
- ✓ Persistent storage (ChromaDB keeps embeddings)
- ✓ Simple codebase (~300 lines total)

Run time for 100 projects: **1-3 hours** (depending on model size)

Start with this, validate quality on 10 projects, then scale to your full set.
