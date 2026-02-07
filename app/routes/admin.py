from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlmodel import Session, select

from ..db import get_session
from ..models import ReportDB, SeriesDB, UserDB
from ..security import TokenPayload, require_role

router = APIRouter()


@router.get("/metrics")
def admin_metrics(
    session: Session = Depends(get_session),
    _: TokenPayload = Depends(require_role("admin")),
) -> dict[str, int]:
    """Return basic counts for admins."""
    series_count = session.exec(select(func.count()).select_from(SeriesDB)).one()
    report_count = session.exec(select(func.count()).select_from(ReportDB)).one()
    user_count = session.exec(select(func.count()).select_from(UserDB)).one()
    return {
        "series": series_count,
        "reports": report_count,
        "users": user_count,
    }
