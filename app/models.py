from typing import Optional

from sqlmodel import Field, SQLModel


class SeriesBase(SQLModel):
    title: str
    creator: str
    year: int
    rating: Optional[float] = None


class Series(SeriesBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class SeriesCreate(SeriesBase):
    pass

