"""SQLAlchemy models for the project database."""
from datetime import datetime
from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class Project(Base):
    """Model representing a project.

    Attributes:
        id: Primary key
        name: Project name (required)
        path: Filesystem path to the project (required)
        readme_path: Path to README.md file (optional)
        logseq_page: Reference to Logseq page (optional)
        github_url: GitHub repository URL (optional)
        is_private: Whether the GitHub repo is private (optional)
        created_at: Timestamp when record was created (auto-set)
        updated_at: Timestamp when record was last updated (auto-updated)
        last_file_modified: Most recent file modification time in project directory (optional)
    """
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    path: Mapped[str] = mapped_column(String(1024), nullable=False)
    readme_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    logseq_page: Mapped[str | None] = mapped_column(String(512), nullable=True)
    github_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_private: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    last_file_modified: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        """Return string representation of Project."""
        return f"Project(name={self.name!r}, path={self.path!r})"
