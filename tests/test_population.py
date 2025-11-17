"""Tests for database population."""
import pytest
from pathlib import Path
from project_database.database import init_database, get_session
from project_database.scanner import populate_database
from project_database.models import Project


def test_populate_database_adds_new_project(tmp_path, monkeypatch):
    """Test that populate_database adds a new project to the database."""
    # Setup database
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    init_database()

    # Create a project directory
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    project_dir = projects_dir / "test-project"
    project_dir.mkdir()

    # Populate database
    populate_database(projects_dir)

    # Verify project was added
    session = get_session()
    projects = session.query(Project).all()
    assert len(projects) == 1
    assert projects[0].name == "test-project"
    assert projects[0].path == str(project_dir)
    session.close()
