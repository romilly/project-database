"""Project scanning and metadata extraction functions."""
import re
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote
from typing import Optional


def parse_logseq_link(link_file: Path) -> str | None:
    """Parse logseq page reference from a Link.md file.

    Args:
        link_file: Path to Link.md file

    Returns:
        The logseq page name (URL-decoded), or None if file doesn't exist
        or doesn't contain a valid logseq link.

    Example:
        Given Link.md containing:
        [logseq](logseq://graph/logseq-personal?page=project%2Fmy-project)

        Returns: "project/my-project"
    """
    # Check if file exists
    if not link_file.exists():
        return None

    try:
        # Read file content
        content = link_file.read_text().strip()

        # Pattern to match logseq URL and extract page parameter
        # Format: [logseq](logseq://graph/NAME?page=PAGE_NAME)
        pattern = r'\[logseq\]\(logseq://graph/[^?]+\?page=([^)]+)\)'
        match = re.search(pattern, content)

        if not match:
            return None

        # Extract and URL-decode the page name
        page_name = match.group(1)
        return unquote(page_name)

    except Exception:
        # If any error occurs (can't read file, etc.), return None
        return None


def get_github_url(remote_url: Optional[str]) -> Optional[str]:
    """Extract GitHub URL from a git remote URL.

    Args:
        remote_url: Git remote URL (HTTPS or SSH format)

    Returns:
        GitHub HTTPS URL without .git extension, or None if not a GitHub URL

    Examples:
        >>> get_github_url("https://github.com/user/repo.git")
        'https://github.com/user/repo'

        >>> get_github_url("git@github.com:user/repo.git")
        'https://github.com/user/repo'

        >>> get_github_url("https://gitlab.com/user/repo.git")
        None
    """
    if not remote_url:
        return None

    # Check if it's a GitHub URL
    if 'github.com' not in remote_url:
        return None

    # Handle HTTPS format: https://github.com/user/repo.git
    https_pattern = r'https://github\.com/([^/]+)/([^/]+?)(\.git)?$'
    match = re.match(https_pattern, remote_url)
    if match:
        user, repo = match.group(1), match.group(2)
        return f"https://github.com/{user}/{repo}"

    # Handle SSH format: git@github.com:user/repo.git
    ssh_pattern = r'git@github\.com:([^/]+)/([^/]+?)(\.git)?$'
    match = re.match(ssh_pattern, remote_url)
    if match:
        user, repo = match.group(1), match.group(2)
        return f"https://github.com/{user}/{repo}"

    return None


def get_last_file_modified_time(project_dir: Path) -> Optional[datetime]:
    """Find the most recent file modification time in a project directory.

    Uses the 'find' command for fast scanning, excluding certain directories
    (venv, .git, __pycache__, node_modules, .idea, .pytest_cache).

    Args:
        project_dir: Path to project directory

    Returns:
        datetime of the most recent file modification, or None if no files found

    Example:
        >>> last_mod = get_last_file_modified_time(Path("/path/to/project"))
        >>> print(last_mod)
        2025-11-18 15:30:45.123456
    """
    # Directories to exclude from scanning
    excluded_dirs = ['venv', '.git', '__pycache__', 'node_modules', '.idea', '.pytest_cache', '.venv']

    try:
        # Build find command with exclusions
        # find /path -type f \( -path '*/venv/*' -o -path '*/.git/*' ... \) -prune -o -type f -printf '%T@\n'
        find_cmd = ['find', str(project_dir), '-type', 'd']

        # Add exclusions: -path '*/dirname/*' -prune for each excluded directory
        prune_args = []
        for i, excluded in enumerate(excluded_dirs):
            if i > 0:
                prune_args.append('-o')
            prune_args.extend(['-path', f'*/{excluded}/*'])

        find_cmd.extend(['('] + prune_args + [')', '-prune', '-o', '-type', 'f', '-printf', '%T@\\n'])

        # Run find command
        result = subprocess.run(
            find_cmd,
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )

        if result.returncode != 0 or not result.stdout.strip():
            return None

        # Parse timestamps and find the maximum
        timestamps = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    timestamps.append(float(line))
                except ValueError:
                    continue

        if not timestamps:
            return None

        # Convert the maximum timestamp to datetime
        max_timestamp = max(timestamps)
        return datetime.fromtimestamp(max_timestamp)

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, Exception):
        # If find command fails, return None
        return None


def collect_project_metadata(project_dir: Path) -> dict:
    """Collect metadata from a project directory.

    Args:
        project_dir: Path to project directory

    Returns:
        Dictionary with project metadata (name, path, readme_path, logseq_page, github_url, last_file_modified)
    """
    # Check for README.md
    readme = project_dir / "README.md"
    readme_path = str(readme) if readme.exists() else None

    # Parse Link.md for logseq page
    link_file = project_dir / "Link.md"
    logseq_page = parse_logseq_link(link_file)

    # Get git remote URL and extract GitHub URL
    github_url = None
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            remote_url = result.stdout.strip()
            github_url = get_github_url(remote_url)
    except Exception:
        # If git command fails or times out, github_url remains None
        pass

    # Get most recent file modification time
    last_file_modified = get_last_file_modified_time(project_dir)

    return {
        "name": project_dir.name,
        "path": str(project_dir),
        "readme_path": readme_path,
        "logseq_page": logseq_page,
        "github_url": github_url,
        "last_file_modified": last_file_modified
    }


def scan_projects_directory(parent_dir: Path) -> list[Path]:
    """Scan a directory and return all direct subdirectories as project paths.

    Excludes the .claude directory (used by Claude Code for workspace configuration).

    Args:
        parent_dir: Parent directory containing projects (e.g., ~/git/active)

    Returns:
        List of Path objects for each direct subdirectory (excluding .claude)
    """
    projects = []
    for item in parent_dir.iterdir():
        if item.is_dir() and item.name != ".claude":
            projects.append(item)
    return projects


def populate_database(parent_dir: Path) -> None:
    """Scan a directory and populate database with all projects.

    For each direct subdirectory, collects metadata and adds/updates
    the project in the database.

    Args:
        parent_dir: Parent directory containing projects (e.g., ~/git/active)
    """
    from project_database.database import get_session
    from project_database.models import Project

    # Scan for projects
    project_dirs = scan_projects_directory(parent_dir)

    # Get database session
    session = get_session()

    try:
        for project_dir in project_dirs:
            # Collect metadata
            metadata = collect_project_metadata(project_dir)

            # Check if project already exists (by path)
            existing = session.query(Project).filter_by(path=metadata["path"]).first()

            if existing:
                # Update existing project
                existing.name = metadata["name"]
                existing.readme_path = metadata["readme_path"]
                existing.logseq_page = metadata["logseq_page"]
                existing.github_url = metadata["github_url"]
                existing.last_file_modified = metadata["last_file_modified"]
            else:
                # Add new project
                project = Project(
                    name=metadata["name"],
                    path=metadata["path"],
                    readme_path=metadata["readme_path"],
                    logseq_page=metadata["logseq_page"],
                    github_url=metadata["github_url"],
                    last_file_modified=metadata["last_file_modified"]
                )
                session.add(project)

        # Commit all changes
        session.commit()
    finally:
        session.close()
