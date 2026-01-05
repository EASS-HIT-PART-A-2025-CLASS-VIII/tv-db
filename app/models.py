from typing import Optional

from sqlmodel import Field, SQLModel


class SeriesBase(SQLModel):
    """Shared series attributes."""

    title: str = Field(min_length=1)
    creator: str = Field(min_length=1)
    year: int = Field(ge=1900, le=2100)
    rating: Optional[float] = Field(default=None, ge=0, le=10)


class Series(SeriesBase):
    """Public model returned by the API."""

    id: int


class SeriesCreate(SeriesBase):
    """Payload for creating a series."""

    pass


class SeriesUpdate(SQLModel):
    """Payload for partial series updates."""

    title: Optional[str] = Field(default=None, min_length=1)
    creator: Optional[str] = Field(default=None, min_length=1)
    year: Optional[int] = Field(default=None, ge=1900, le=2100)
    rating: Optional[float] = Field(default=None, ge=0, le=10)


class SeriesDB(SeriesBase, table=True):
    """Database table model."""

    id: Optional[int] = Field(default=None, primary_key=True)
