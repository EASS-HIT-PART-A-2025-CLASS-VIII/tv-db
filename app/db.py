from contextlib import contextmanager
import os
from typing import Iterator

from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./series.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def create_db_and_tables() -> None:
    """Create database tables if they do not exist."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    """Yield a short-lived database session per call."""
    with Session(engine) as session:
        yield session


@contextmanager
def session_context() -> Iterator[Session]:
    """Context manager for scripts/CLI usage."""
    with Session(engine) as session:
        yield session
