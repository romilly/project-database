"""Tests for the Project model."""
import pytest
import time
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from project_database.models import Base, Project


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_create_project_with_all_fields(db_session):
    """Test creating a project with all fields populated."""
    project = Project(
        name="test-project",
        path="/home/romilly/git/active/test-project",
        readme_path="/home/romilly/git/active/test-project/README.md",
        logseq_page="project/test-project",
        github_url="https://github.com/romilly/test-project",
        is_private=False
    )

    db_session.add(project)
    db_session.commit()

    # Retrieve the project
    retrieved = db_session.query(Project).filter_by(name="test-project").first()

    assert retrieved is not None
    assert retrieved.name == "test-project"
    assert retrieved.path == "/home/romilly/git/active/test-project"
    assert retrieved.readme_path == "/home/romilly/git/active/test-project/README.md"
    assert retrieved.logseq_page == "project/test-project"
    assert retrieved.github_url == "https://github.com/romilly/test-project"
    assert retrieved.is_private is False


def test_create_project_with_minimal_fields(db_session):
    """Test creating a project with only required fields (name and path)."""
    project = Project(
        name="minimal-project",
        path="/home/romilly/git/active/minimal-project"
    )

    db_session.add(project)
    db_session.commit()

    # Retrieve the project
    retrieved = db_session.query(Project).filter_by(name="minimal-project").first()

    assert retrieved is not None
    assert retrieved.name == "minimal-project"
    assert retrieved.path == "/home/romilly/git/active/minimal-project"
    assert retrieved.readme_path is None
    assert retrieved.logseq_page is None
    assert retrieved.github_url is None
    assert retrieved.is_private is None


def test_created_at_timestamp_auto_set(db_session):
    """Test that created_at is automatically set when a project is created."""
    before_create = datetime.now()

    project = Project(
        name="timestamp-test",
        path="/home/romilly/git/active/timestamp-test"
    )

    db_session.add(project)
    db_session.commit()

    after_create = datetime.now()

    # Retrieve the project
    retrieved = db_session.query(Project).filter_by(name="timestamp-test").first()

    assert retrieved is not None
    assert retrieved.created_at is not None
    assert isinstance(retrieved.created_at, datetime)
    # Check that created_at is between before and after timestamps
    assert before_create <= retrieved.created_at <= after_create


def test_updated_at_timestamp_auto_updates(db_session):
    """Test that updated_at is automatically updated when a project is modified."""
    # Create project
    project = Project(
        name="update-test",
        path="/home/romilly/git/active/update-test"
    )

    db_session.add(project)
    db_session.commit()

    # Get initial timestamps
    retrieved = db_session.query(Project).filter_by(name="update-test").first()
    initial_created_at = retrieved.created_at
    initial_updated_at = retrieved.updated_at

    assert initial_updated_at is not None
    assert isinstance(initial_updated_at, datetime)

    # Wait a moment to ensure timestamp difference
    time.sleep(0.1)

    # Update the project
    retrieved.name = "update-test-modified"
    db_session.commit()

    # Get timestamps after update
    db_session.expire(retrieved)  # Force reload from database
    updated_retrieved = db_session.query(Project).filter_by(name="update-test-modified").first()

    # created_at should not change
    assert updated_retrieved.created_at == initial_created_at

    # updated_at should change
    assert updated_retrieved.updated_at > initial_updated_at


def test_last_file_modified_timestamp_can_be_set(db_session):
    """Test that last_file_modified can be explicitly set."""
    # Create a specific datetime for file modification
    file_mod_time = datetime(2025, 11, 15, 10, 30, 0)

    project = Project(
        name="file-mod-test",
        path="/home/romilly/git/active/file-mod-test",
        last_file_modified=file_mod_time
    )

    db_session.add(project)
    db_session.commit()

    # Retrieve and verify
    retrieved = db_session.query(Project).filter_by(name="file-mod-test").first()

    assert retrieved is not None
    assert retrieved.last_file_modified is not None
    assert isinstance(retrieved.last_file_modified, datetime)
    assert retrieved.last_file_modified == file_mod_time