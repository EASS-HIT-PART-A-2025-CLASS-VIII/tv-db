from sqlmodel import Session, select

from ..models import Report, ReportCreate, ReportDB


def create_report(payload: ReportCreate, session: Session, created_by: str) -> Report:
    """Persist a report record."""
    report = ReportDB.model_validate(
        {
            **payload.model_dump(),
            "created_by": created_by,
        }
    )
    session.add(report)
    session.commit()
    session.refresh(report)
    return Report.model_validate(report)


def list_reports(session: Session, limit: int = 50) -> list[Report]:
    """Return the most recent reports."""
    rows = session.exec(select(ReportDB).order_by(ReportDB.created_at.desc()).limit(limit)).all()
    return [Report.model_validate(row) for row in rows]


def latest_report(session: Session) -> Report | None:
    """Return the latest report if present."""
    row = session.exec(select(ReportDB).order_by(ReportDB.created_at.desc()).limit(1)).first()
    return Report.model_validate(row) if row else None
