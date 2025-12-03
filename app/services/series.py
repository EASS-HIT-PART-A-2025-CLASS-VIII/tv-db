from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..models import Series, SeriesCreate, SeriesDB


def _find_duplicate_series(series: SeriesCreate, session: Session) -> SeriesDB | None:
    """Return an existing series that matches the full payload, if any."""
    return session.exec(
        select(SeriesDB).where(
            SeriesDB.title == series.title,
            SeriesDB.creator == series.creator,
            SeriesDB.year == series.year,
            SeriesDB.rating == series.rating,
        )
    ).first()


def list_series(session: Session) -> list[Series]:
    rows = session.exec(select(SeriesDB).order_by(SeriesDB.id)).all()
    return [Series.model_validate(row) for row in rows]


def create_series(series: SeriesCreate, session: Session) -> Series:
    if existing := _find_duplicate_series(series, session):
        return Series.model_validate(existing)

    db_series = SeriesDB.model_validate(series)
    session.add(db_series)
    session.commit()
    session.refresh(db_series)
    return Series.model_validate(db_series)


def get_series(series_id: int, session: Session) -> Series:
    series = session.get(SeriesDB, series_id)
    if series is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Series not found")
    return Series.model_validate(series)


def delete_series(series_id: int, session: Session) -> None:
    series = session.get(SeriesDB, series_id)
    if series is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Series not found")

    session.delete(series)
    session.commit()
    return None


def find_duplicate_series(series: SeriesCreate, session: Session) -> SeriesDB | None:
    """Public wrapper kept for callers like CLI seed."""
    return _find_duplicate_series(series, session)
