"""Tests for AST-based code analyzer."""

from pathlib import Path
from project_database.readme_generation.ast_analyzer import CodeAnalyzer


# Test fixtures path
FIXTURES_DIR = Path(__file__).parent / 'fixtures'
SAMPLE_MODULE = FIXTURES_DIR / 'sample_module.py'
SYNTAX_ERROR_FILE = FIXTURES_DIR / 'syntax_error.py'


def test_analyze_file_extracts_functions():
    """Should extract all function definitions including methods."""
    analyzer = CodeAnalyzer()
    result = analyzer.analyze_file(str(SAMPLE_MODULE))

    assert 'functions' in result
    functions = result['functions']
    # Should extract 2 standalone functions + 3 methods = 5 total
    assert len(functions) == 5

    # Check first standalone function
    func_names = [f['name'] for f in functions]
    assert 'simple_function' in func_names
    assert 'another_function' in func_names
    assert 'method_one' in func_names
    assert 'method_two' in func_names
    assert 'child_method' in func_names

    # Verify one function in detail
    simple_func = [f for f in functions if f['name'] == 'simple_function'][0]
    assert simple_func['args'] == ['arg1', 'arg2']
    assert 'A simple function' in simple_func['docstring']
    assert simple_func['lineno'] == 8


def test_analyze_file_extracts_classes():
    """Should extract class definitions from a file."""
    analyzer = CodeAnalyzer()
    result = analyzer.analyze_file(str(SAMPLE_MODULE))

    assert 'classes' in result
    classes = result['classes']
    assert len(classes) == 2

    # Check first class
    cls1 = classes[0]
    assert cls1['name'] == 'SampleClass'
    assert cls1['bases'] == []
    assert 'method_one' in cls1['methods']
    assert 'method_two' in cls1['methods']
    assert 'A sample class' in cls1['docstring']

    # Check second class (inherits from first)
    cls2 = classes[1]
    assert cls2['name'] == 'ChildClass'
    assert 'SampleClass' in cls2['bases']
    assert 'child_method' in cls2['methods']


def test_analyze_file_extracts_imports():
    """Should extract import statements from a file."""
    analyzer = CodeAnalyzer()
    result = analyzer.analyze_file(str(SAMPLE_MODULE))

    assert 'imports' in result
    imports = result['imports']
    assert 'os' in imports
    assert 'sys' in imports
    assert 'pathlib.Path' in imports


def test_analyze_file_extracts_module_docstring():
    """Should extract module-level docstring."""
    analyzer = CodeAnalyzer()
    result = analyzer.analyze_file(str(SAMPLE_MODULE))

    assert 'module_docstring' in result
    assert 'Sample module for testing' in result['module_docstring']


def test_analyze_file_includes_source():
    """Should include the full source code."""
    analyzer = CodeAnalyzer()
    result = analyzer.analyze_file(str(SAMPLE_MODULE))

    assert 'source' in result
    assert 'def simple_function' in result['source']
    assert 'class SampleClass' in result['source']


def test_analyze_file_handles_syntax_error():
    """Should handle files with syntax errors gracefully."""
    analyzer = CodeAnalyzer()
    result = analyzer.analyze_file(str(SYNTAX_ERROR_FILE))

    assert 'error' in result
    assert result['error'] == 'syntax_error'
    assert result['filepath'] == str(SYNTAX_ERROR_FILE)


def test_analyze_file_includes_filepath():
    """Should include the filepath in the result."""
    analyzer = CodeAnalyzer()
    result = analyzer.analyze_file(str(SAMPLE_MODULE))

    assert 'filepath' in result
    assert result['filepath'] == str(SAMPLE_MODULE)


def test_analyze_project_finds_python_files():
    """Should analyze all Python files in a directory."""
    analyzer = CodeAnalyzer()
    result = analyzer.analyze_project(str(FIXTURES_DIR))

    assert 'project_name' in result
    assert result['project_name'] == 'fixtures'

    assert 'file_count' in result
    # Should find sample_module.py but skip syntax_error.py
    assert result['file_count'] == 1

    assert 'files' in result
    assert len(result['files']) == 1


def test_analyze_project_aggregates_statistics():
    """Should provide aggregate statistics about the project."""
    analyzer = CodeAnalyzer()
    result = analyzer.analyze_project(str(FIXTURES_DIR))

    assert 'total_functions' in result
    # 2 standalone functions + 3 methods = 5 total
    assert result['total_functions'] == 5

    assert 'total_classes' in result
    assert result['total_classes'] == 2

    assert 'all_imports' in result
    assert 'os' in result['all_imports']
    assert 'sys' in result['all_imports']