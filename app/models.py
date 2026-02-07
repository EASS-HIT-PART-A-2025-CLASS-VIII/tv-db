from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class SeriesBase(SQLModel):
    """Shared series attributes."""

    title: str = Field(min_length=1)
    creator: str = Field(min_length=1)
    year: int = Field(ge=1900, le=2100)
    rating: float | None = Field(default=None, ge=0, le=10)


class Series(SeriesBase):
    """Public model returned by the API."""

    id: int
    last_refreshed_at: datetime | None = None


class SeriesCreate(SeriesBase):
    """Payload for creating a series."""

    pass


class SeriesUpdate(SQLModel):
    """Payload for partial series updates."""

    title: str | None = Field(default=None, min_length=1)
    creator: str | None = Field(default=None, min_length=1)
    year: int | None = Field(default=None, ge=1900, le=2100)
    rating: float | None = Field(default=None, ge=0, le=10)


class SeriesDB(SeriesBase, table=True):
    """Database table model."""

    id: int | None = Field(default=None, primary_key=True)
    last_refreshed_at: datetime | None = Field(default=None)


class UserDB(SQLModel, table=True):
    """Database user for authentication."""

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, min_length=3, sa_column_kwargs={"unique": True})
    hashed_password: str = Field(min_length=1)
    role: str = Field(default="viewer")


class LoginRequest(SQLModel):
    """Payload for requesting an access token."""

    username: str
    password: str


class RegisterRequest(SQLModel):
    """Payload for registering a new viewer account."""

    username: str
    password: str
    password_confirm: str


class SummaryRequest(SQLModel):
    """Payload for requesting an AI summary."""

    series_id: int | None = None


class Token(SQLModel):
    """JWT response payload."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ReportBase(SQLModel):
    """Shared report fields."""

    title: str = Field(min_length=1, max_length=160)
    content: str = Field(min_length=1)


class ReportCreate(ReportBase):
    """Payload for creating a report."""

    pass


class Report(ReportBase):
    """Public report model."""

    id: int
    created_at: datetime
    created_by: str


class ReportDB(ReportBase, table=True):
    """Database report record."""

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = Field(min_length=1, max_length=80)
