"""Tests for database initialization and management."""
import os
import pytest
from pathlib import Path

from project_database.database import init_database, get_session
from project_database.models import Project


def test_init_database_creates_tables(tmp_path, monkeypatch):
    """Test that init_database creates database file and tables."""
    # Set DATABASE_PATH environment variable
    db_path = tmp_path / "test.sqlite"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))

    # Initialize database
    init_database()

    # Check database file was created
    assert db_path.exists()

    # Check we can create a session and query
    session = get_session()
    projects = session.query(Project).all()
    assert projects == []
    session.close()


def test_get_session_returns_working_session(tmp_path, monkeypatch):
    """Test that get_session returns a working database session."""
    # Set DATABASE_PATH environment variable
    db_path = tmp_path / "test.sqlite"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))

    # Initialize and get session
    init_database()
    session = get_session()

    # Add a project
    project = Project(name="test", path="/test/path")
    session.add(project)
    session.commit()

    # Retrieve it
    retrieved = session.query(Project).filter_by(name="test").first()
    assert retrieved is not None
    assert retrieved.name == "test"

    session.close()
