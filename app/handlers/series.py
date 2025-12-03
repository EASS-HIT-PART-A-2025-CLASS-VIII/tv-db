from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..models import Series, SeriesCreate, SeriesDB
from ..services.series import find_duplicate_series


def list_series(session: Session) -> list[Series]:
    rows = session.exec(select(SeriesDB)).all()
    return [Series.model_validate(row) for row in rows]


def create_series(series: SeriesCreate, session: Session) -> Series:
    if existing := find_duplicate_series(series, session):
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
