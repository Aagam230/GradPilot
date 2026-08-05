from typing import Optional

from sqlalchemy.orm import Session

from ...models import HistoricalApplication
from .normalization import normalize_application_record


def create_historical_application(
    db: Session,
    record: dict,
) -> HistoricalApplication:
    """
    Normalize and store one historical application.
    """

    normalized = normalize_application_record(record)

    if not normalized.get("canonical_university"):
        raise ValueError("canonical_university is required")

    if not normalized.get("canonical_program"):
        raise ValueError("canonical_program is required")

    if not normalized.get("decision"):
        raise ValueError(
            "decision must resolve to admitted, rejected, or waitlisted"
        )

    application = HistoricalApplication(**normalized)

    db.add(application)
    db.commit()
    db.refresh(application)

    return application


def get_historical_applications(
    db: Session,
    canonical_university: str,
    canonical_program: str,
    years: Optional[list[int]] = None,
    decisions: Optional[list[str]] = None,
    limit: int = 1000,
) -> list[HistoricalApplication]:
    """
    Retrieve historical applications for one canonical program.
    """

    query = db.query(HistoricalApplication).filter(
        HistoricalApplication.canonical_university
        == canonical_university,
        HistoricalApplication.canonical_program
        == canonical_program,
    )

    if years:
        query = query.filter(
            HistoricalApplication.application_year.in_(years)
        )

    if decisions:
        query = query.filter(
            HistoricalApplication.decision.in_(decisions)
        )

    return (
        query
        .order_by(HistoricalApplication.application_year.desc())
        .limit(limit)
        .all()
    )


def count_historical_applications(
    db: Session,
    canonical_university: str,
    canonical_program: str,
) -> dict:
    """
    Return decision counts for one canonical program.
    """

    records = get_historical_applications(
        db=db,
        canonical_university=canonical_university,
        canonical_program=canonical_program,
    )

    counts = {
        "total": len(records),
        "admitted": 0,
        "rejected": 0,
        "waitlisted": 0,
    }

    for record in records:
        if record.decision in counts:
            counts[record.decision] += 1

    return counts