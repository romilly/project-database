"""Code chunker for splitting code at function/class boundaries."""

from pathlib import Path
from typing import Dict, List, Any


class CodeChunker:
    """Chunk code at function/class boundaries for embedding."""

    def chunk_file(self, file_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create chunks from analyzed file.

        Args:
            file_info: Dictionary from CodeAnalyzer.analyze_file()

        Returns:
            List of chunk dictionaries, each with type, filepath, content, and metadata
        """
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
    """
    Chunk all files in analyzed project.

    Args:
        project_info: Dictionary from CodeAnalyzer.analyze_project()

    Returns:
        List of all chunks from all files in the project
    """
    chunker = CodeChunker()
    all_chunks = []

    for file_info in project_info['files']:
        chunks = chunker.chunk_file(file_info)
        all_chunks.extend(chunks)

    return all_chunks