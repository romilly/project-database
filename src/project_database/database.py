"""Database initialization and session management."""
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from project_database.models import Base

# Global engine and session maker
_engine = None
_SessionMaker = None


def init_database() -> None:
    """Initialize the database from environment configuration.

    Reads DATABASE_PATH from environment variables, creates the database file
    and all tables defined in the models.

    Note: Call load_dotenv() before this function to load from .env file.
    """
    global _engine, _SessionMaker

    # Get database path from environment
    db_path = os.getenv("DATABASE_PATH")
    if not db_path:
        raise ValueError("DATABASE_PATH not found in environment")

    # Create parent directory if it doesn't exist
    db_path_obj = Path(db_path)
    db_path_obj.parent.mkdir(parents=True, exist_ok=True)

    # Close existing engine if any
    if _engine is not None:
        _engine.dispose()

    # Create engine and tables
    _engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(_engine)

    # Create session maker
    _SessionMaker = sessionmaker(bind=_engine)


def get_session() -> Session:
    """Get a database session.

    Returns:
        A SQLAlchemy session for database operations.

    Raises:
        RuntimeError: If database has not been initialized.
    """
    if _SessionMaker is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")

    return _SessionMaker()
