from typing import Annotated

from fastapi import APIRouter, Body, Depends
from sqlmodel import Session

from ..ai import SummaryResult, generate_summary
from ..db import get_session
from ..models import SummaryRequest
from ..security import TokenPayload, require_role
from ..services import series as series_service

router = APIRouter()
SessionDep = Annotated[Session, Depends(get_session)]


@router.post("/summary", response_model=SummaryResult)
async def summary(
    session: SessionDep,
    _: TokenPayload = Depends(require_role("admin", "viewer")),
    payload: SummaryRequest | None = Body(default=None),
) -> SummaryResult:
    """Generate an AI summary of the series catalog."""
    if payload and payload.series_id is not None:
        rows = [series_service.get_series(payload.series_id, session)]
    else:
        rows = series_service.list_series(session, offset=0, limit=200)
    return await generate_summary(rows)
