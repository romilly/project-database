"""Tests for project scanning and metadata extraction."""
import pytest
import subprocess
from pathlib import Path
from project_database.scanner import parse_logseq_link, get_github_url, collect_project_metadata


def test_parse_logseq_link_from_file(tmp_path):
    """Test parsing logseq page reference from Link.md file."""
    # Create a Link.md file with logseq URL
    link_file = tmp_path / "Link.md"
    link_file.write_text("[logseq](logseq://graph/logseq-personal?page=project%2Fproject-database)")

    # Parse it
    logseq_page = parse_logseq_link(link_file)

    # Should extract and URL-decode the page name
    assert logseq_page == "project/project-database"


def test_parse_logseq_link_with_complex_page_name(tmp_path):
    """Test parsing logseq link with URL-encoded characters."""
    link_file = tmp_path / "Link.md"
    link_file.write_text("[logseq](logseq://graph/logseq-personal?page=project%2Fmy-cool%20project)")

    logseq_page = parse_logseq_link(link_file)

    assert logseq_page == "project/my-cool project"


def test_parse_logseq_link_file_not_found():
    """Test parsing when Link.md doesn't exist."""
    logseq_page = parse_logseq_link(Path("/nonexistent/Link.md"))

    assert logseq_page is None


def test_parse_logseq_link_invalid_format(tmp_path):
    """Test parsing when Link.md has invalid format."""
    link_file = tmp_path / "Link.md"
    link_file.write_text("Just some random text")

    logseq_page = parse_logseq_link(link_file)

    assert logseq_page is None


def test_get_github_url_https_format():
    """Test extracting GitHub URL from HTTPS remote."""
    remote_url = "https://github.com/romilly/project-database.git"
    github_url = get_github_url(remote_url)
    assert github_url == "https://github.com/romilly/project-database"


def test_get_github_url_ssh_format():
    """Test extracting GitHub URL from SSH remote."""
    remote_url = "git@github.com:romilly/project-database.git"
    github_url = get_github_url(remote_url)
    assert github_url == "https://github.com/romilly/project-database"


def test_get_github_url_non_github_remote():
    """Test with non-GitHub remote returns None."""
    remote_url = "https://gitlab.com/user/project.git"
    github_url = get_github_url(remote_url)
    assert github_url is None


def test_get_github_url_none():
    """Test with None input returns None."""
    github_url = get_github_url(None)
    assert github_url is None


def test_get_last_file_modified_time(tmp_path):
    """Test finding the most recent file modification time in a directory."""
    from project_database.scanner import get_last_file_modified_time
    from datetime import datetime
    import time

    # Create a project directory with some files
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()

    # Create an old file
    old_file = project_dir / "old.txt"
    old_file.write_text("old")
    old_time = datetime.fromtimestamp(old_file.stat().st_mtime)

    # Wait a bit
    time.sleep(0.1)

    # Create a newer file
    new_file = project_dir / "new.txt"
    new_file.write_text("new")
    new_time = datetime.fromtimestamp(new_file.stat().st_mtime)

    # Get the most recent modification time
    last_modified = get_last_file_modified_time(project_dir)

    # Should return the newer time
    assert last_modified is not None
    assert last_modified >= old_time
    assert abs((last_modified - new_time).total_seconds()) < 1  # Within 1 second


def test_get_last_file_modified_time_excludes_venv(tmp_path):
    """Test that venv directory is excluded from file modification scan."""
    from project_database.scanner import get_last_file_modified_time
    from datetime import datetime
    import time

    # Create project directory
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()

    # Create a file in the main directory
    main_file = project_dir / "main.txt"
    main_file.write_text("main")
    main_time = datetime.fromtimestamp(main_file.stat().st_mtime)

    time.sleep(0.1)

    # Create venv directory with a newer file (should be ignored)
    venv_dir = project_dir / "venv"
    venv_dir.mkdir()
    venv_file = venv_dir / "newer.txt"
    venv_file.write_text("newer in venv")

    # Get the most recent modification time
    last_modified = get_last_file_modified_time(project_dir)

    # Should return main_time, not the venv file time
    assert last_modified is not None
    assert abs((last_modified - main_time).total_seconds()) < 1  # Within 1 second
