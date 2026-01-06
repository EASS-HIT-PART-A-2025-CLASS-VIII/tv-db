from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..models import Series, SeriesCreate, SeriesDB, SeriesUpdate
from .helpers import find_duplicate_series


def list_series(session: Session, offset: int = 0, limit: int = 100) -> list[Series]:
    """Return series ordered by ID with pagination."""
    rows = session.exec(select(SeriesDB).order_by(SeriesDB.id).offset(offset).limit(limit)).all()
    return [Series.model_validate(row) for row in rows]


def create_series(series: SeriesCreate, session: Session) -> Series:
    """Create a new series or return an existing duplicate."""
    if existing := find_duplicate_series(series, session):
        return Series.model_validate(existing)

    db_series = SeriesDB.model_validate(series)
    session.add(db_series)
    session.commit()
    session.refresh(db_series)
    return Series.model_validate(db_series)


def get_series(series_id: int, session: Session) -> Series:
    """Fetch a series by ID or raise a 404."""
    series = session.get(SeriesDB, series_id)
    if series is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Series not found")
    return Series.model_validate(series)


def update_series(series_id: int, payload: SeriesCreate, session: Session) -> Series:
    """Replace a series record with the provided payload."""
    series = session.get(SeriesDB, series_id)
    if series is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Series not found")

    series.title = payload.title
    series.creator = payload.creator
    series.year = payload.year
    series.rating = payload.rating
    session.add(series)
    session.commit()
    session.refresh(series)
    return Series.model_validate(series)


def patch_series(series_id: int, payload: SeriesUpdate, session: Session) -> Series:
    """Apply partial updates to a series record."""
    series = session.get(SeriesDB, series_id)
    if series is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Series not found")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(series, field, value)

    session.add(series)
    session.commit()
    session.refresh(series)
    return Series.model_validate(series)


def delete_series(series_id: int, session: Session) -> None:
    """Delete a series by ID."""
    series = session.get(SeriesDB, series_id)
    if series is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Series not found")

    session.delete(series)
    session.commit()
