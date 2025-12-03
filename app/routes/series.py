from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from ..db import get_session
from ..handlers import series as handlers
from ..models import Series, SeriesCreate

router = APIRouter()
SessionDep = Annotated[Session, Depends(get_session)]


@router.get("", response_model=list[Series])
def list_series(session: SessionDep) -> list[Series]:
    return handlers.list_series(session)


@router.post("", response_model=Series, status_code=status.HTTP_201_CREATED)
def create_series(series: SeriesCreate, session: SessionDep) -> Series:
    return handlers.create_series(series, session)


@router.get("/{series_id}", response_model=Series)
def get_series(series_id: int, session: SessionDep) -> Series:
    return handlers.get_series(series_id, session)


@router.delete("/{series_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_series(series_id: int, session: SessionDep) -> None:
    return handlers.delete_series(series_id, session)
