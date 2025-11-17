"""Tests for directory scanning."""
import pytest
from pathlib import Path
from project_database.scanner import scan_projects_directory


def test_scan_finds_direct_subdirectories(tmp_path):
    """Test that scan_projects_directory finds all direct subdirectories."""
    # Create a parent directory with some project subdirectories
    parent = tmp_path / "projects"
    parent.mkdir()

    proj1 = parent / "project-one"
    proj1.mkdir()
    proj2 = parent / "project-two"
    proj2.mkdir()
    proj3 = parent / "project-three"
    proj3.mkdir()

    # Scan the parent directory
    projects = scan_projects_directory(parent)

    # Should find all three projects
    assert len(projects) == 3
    assert proj1 in projects
    assert proj2 in projects
    assert proj3 in projects
