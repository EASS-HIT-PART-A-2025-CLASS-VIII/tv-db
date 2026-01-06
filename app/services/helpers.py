from sqlmodel import Session, select

from ..models import SeriesCreate, SeriesDB


def find_duplicate_series(series: SeriesCreate, session: Session) -> SeriesDB | None:
    """Return an existing series that matches the identity fields, if any."""
    return session.exec(
        select(SeriesDB).where(
            SeriesDB.title == series.title,
            SeriesDB.creator == series.creator,
            SeriesDB.year == series.year,
        )
    ).first()
