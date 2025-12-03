from typing import Optional

from sqlmodel import Field, SQLModel


class SeriesBase(SQLModel):
    title: str = Field(min_length=1)
    creator: str = Field(min_length=1)
    year: int = Field(ge=1900, le=2100)
    rating: Optional[float] = Field(default=None, ge=0, le=10)


class Series(SeriesBase):
    """Public model returned by the API."""

    id: int


class SeriesCreate(SeriesBase):
    pass


class SeriesDB(SeriesBase, table=True):
    """Database table model."""

    id: Optional[int] = Field(default=None, primary_key=True)
