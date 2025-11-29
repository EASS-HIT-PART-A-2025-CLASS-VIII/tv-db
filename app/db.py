from contextlib import contextmanager
from typing import Iterator

from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = "sqlite:///./series.db"
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


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
