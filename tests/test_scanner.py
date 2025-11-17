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
