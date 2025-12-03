from typing import Optional

from sqlmodel import Field, SQLModel


class SeriesBase(SQLModel):
    title: str
    creator: str
    year: int
    rating: Optional[float] = None


class Series(SeriesBase):
    """Public model returned by the API."""

    id: int


class SeriesCreate(SeriesBase):
    pass


class SeriesDB(SeriesBase, table=True):
    """Database table model."""

    id: Optional[int] = Field(default=None, primary_key=True)
