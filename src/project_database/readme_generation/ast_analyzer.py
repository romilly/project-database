"""AST-based code analyzer for extracting structural information from Python files."""

import ast
from pathlib import Path
from typing import Dict, List, Any


class CodeAnalyzer:
    """Extract structural information from Python files using AST."""

    def analyze_file(self, filepath: str) -> Dict[str, Any]:
        """
        Parse a single Python file and extract metadata.

        Args:
            filepath: Path to the Python file to analyze

        Returns:
            Dictionary containing functions, classes, imports, docstring, and source code.
            If syntax error occurs, returns dict with 'error' key.
        """
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
                    'docstring': ast.get_docstring(node) or '',
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
                    'docstring': ast.get_docstring(node) or '',
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
        """
        Analyze all Python files in a project.

        Args:
            project_path: Path to the project directory

        Returns:
            Dictionary containing project metadata and analysis of all files
        """
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