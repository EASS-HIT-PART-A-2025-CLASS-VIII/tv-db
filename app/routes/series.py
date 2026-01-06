from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from ..db import get_session
from ..models import Series, SeriesCreate, SeriesUpdate
from ..services import series as service

router = APIRouter()
SessionDep = Annotated[Session, Depends(get_session)]


@router.get("", response_model=list[Series])
def list_series(
    session: SessionDep,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> list[Series]:
    """List all series entries."""
    return service.list_series(session, offset=offset, limit=limit)


@router.post("", response_model=Series, status_code=status.HTTP_201_CREATED)
def create_series(series: SeriesCreate, session: SessionDep) -> Series:
    """Create a new series entry."""
    return service.create_series(series, session)


@router.get("/{series_id}", response_model=Series)
def get_series(series_id: int, session: SessionDep) -> Series:
    """Get a series entry by ID."""
    return service.get_series(series_id, session)


@router.put("/{series_id}", response_model=Series)
def update_series(series_id: int, series: SeriesCreate, session: SessionDep) -> Series:
    """Replace a series entry by ID."""
    return service.update_series(series_id, series, session)


@router.patch("/{series_id}", response_model=Series)
def patch_series(series_id: int, series: SeriesUpdate, session: SessionDep) -> Series:
    """Partially update a series entry by ID."""
    return service.patch_series(series_id, series, session)


@router.delete("/{series_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_series(series_id: int, session: SessionDep) -> None:
    """Delete a series entry by ID."""
    return service.delete_series(series_id, session)
