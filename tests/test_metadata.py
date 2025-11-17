"""Tests for project metadata collection."""
import pytest
import subprocess
from pathlib import Path
from project_database.scanner import collect_project_metadata


def test_collect_metadata_gets_name_and_path(tmp_path):
    """Test that collect_project_metadata gets project name and path."""
    project_dir = tmp_path / "my-project"
    project_dir.mkdir()

    metadata = collect_project_metadata(project_dir)

    assert metadata["name"] == "my-project"
    assert metadata["path"] == str(project_dir)


def test_collect_metadata_finds_readme(tmp_path):
    """Test that collect_project_metadata finds README.md if it exists."""
    project_dir = tmp_path / "my-project"
    project_dir.mkdir()
    readme = project_dir / "README.md"
    readme.write_text("# My Project")

    metadata = collect_project_metadata(project_dir)

    assert metadata["readme_path"] == str(readme)


def test_collect_metadata_no_readme(tmp_path):
    """Test that readme_path is None when README.md doesn't exist."""
    project_dir = tmp_path / "my-project"
    project_dir.mkdir()

    metadata = collect_project_metadata(project_dir)

    assert metadata["readme_path"] is None


def test_collect_metadata_parses_link_md(tmp_path):
    """Test that collect_project_metadata parses Link.md for logseq page."""
    project_dir = tmp_path / "my-project"
    project_dir.mkdir()
    link = project_dir / "Link.md"
    link.write_text("[logseq](logseq://graph/logseq-personal?page=project%2Fmy-project)")

    metadata = collect_project_metadata(project_dir)

    assert metadata["logseq_page"] == "project/my-project"


def test_collect_metadata_gets_github_url(tmp_path):
    """Test that collect_project_metadata extracts GitHub URL from git remote."""
    project_dir = tmp_path / "my-project"
    project_dir.mkdir()

    # Initialize git repo with GitHub remote
    subprocess.run(["git", "init"], cwd=project_dir, capture_output=True)
    subprocess.run(["git", "remote", "add", "origin", "https://github.com/romilly/my-project.git"],
                   cwd=project_dir, capture_output=True)

    metadata = collect_project_metadata(project_dir)

    assert metadata["github_url"] == "https://github.com/romilly/my-project"