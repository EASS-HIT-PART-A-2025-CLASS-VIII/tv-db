from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from ..db import get_session
from ..models import Report, ReportCreate
from ..queue import QueueMessage, enqueue_report_job, get_redis
from ..security import TokenPayload, require_role
from ..services import reports as report_service

router = APIRouter()
SessionDep = Annotated[Session, Depends(get_session)]


@router.post("", response_model=Report, status_code=status.HTTP_201_CREATED)
def create_report(
    payload: ReportCreate,
    session: SessionDep,
    token: TokenPayload = Depends(require_role("admin", "worker")),
) -> Report:
    """Create a report record."""
    return report_service.create_report(payload, session, created_by=token.sub)


@router.get("", response_model=list[Report])
def list_reports(
    session: SessionDep,
    token: TokenPayload = Depends(require_role("admin")),
) -> list[Report]:
    """List reports."""
    return report_service.list_reports(session)


@router.post("/queue", response_model=QueueMessage, status_code=status.HTTP_202_ACCEPTED)
async def queue_report(
    token: TokenPayload = Depends(require_role("admin")),
    redis=Depends(get_redis),
) -> QueueMessage:
    """Queue a report job for the worker."""
    return await enqueue_report_job(redis, requested_by=token.sub)
