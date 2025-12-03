from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..models import Series, SeriesCreate


def list_series(session: Session) -> list[Series]:
    return session.exec(select(Series)).all()


def create_series(series: SeriesCreate, session: Session) -> Series:
    db_series = Series.model_validate(series)
    session.add(db_series)
    session.commit()
    session.refresh(db_series)
    return db_series


def get_series(series_id: int, session: Session) -> Series:
    series = session.get(Series, series_id)
    if series is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Series not found")
    return series


def delete_series(series_id: int, session: Session) -> None:
    series = session.get(Series, series_id)
    if series is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Series not found")

    session.delete(series)
    session.commit()
    return None
