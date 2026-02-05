import logging
import os
from contextlib import contextmanager
from typing import Iterator

from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import text

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./series.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
logger = logging.getLogger(__name__)
try:
    engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)
except Exception as exc:
    raise RuntimeError(
        f"Failed to create database engine for DATABASE_URL='{DATABASE_URL}'."
    ) from exc


def create_db_and_tables() -> None:
    """Create database tables if they do not exist."""
    try:
        SQLModel.metadata.create_all(engine)
        if DATABASE_URL.startswith("sqlite"):
            _ensure_sqlite_column("seriesdb", "last_refreshed_at", "DATETIME")
    except Exception as exc:
        logger.exception("Database initialization failed.")
        raise RuntimeError(
            f"Failed to initialize database at DATABASE_URL='{DATABASE_URL}'."
        ) from exc


def get_session() -> Iterator[Session]:
    """Yield a short-lived database session per call."""
    with Session(engine) as session:
        yield session


def _ensure_sqlite_column(table: str, column: str, column_type: str) -> None:
    """Add a column in SQLite if it is missing (simple local dev migration)."""
    with engine.connect() as connection:
        rows = connection.execute(text(f"PRAGMA table_info({table})")).fetchall()
        columns = {row[1] for row in rows}
        if column not in columns:
            connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}"))


@contextmanager
def session_context() -> Iterator[Session]:
    """Context manager for scripts/CLI usage."""
    with Session(engine) as session:
        yield session
