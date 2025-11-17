"""Tests for the Project model."""
import pytest
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