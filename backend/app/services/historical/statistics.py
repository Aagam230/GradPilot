from statistics import median
from typing import Optional
from sqlalchemy.orm import Session
from .repository import get_historical_applications


def _median(values: list) -> Optional[float]:
    clean = [v for v in values if v is not None]
    return round(float(median(clean)), 3) if clean else None


def _percentage_true(values: list) -> Optional[float]:
    known = [v for v in values if v is not None]
    return round((sum(1 for v in known if v) / len(known)) * 100, 1) if known else None


def _cohort_statistics(records: list) -> dict:
    return {
        "sample_size": len(records),
        "median_gpa_normalized": _median([r.gpa_normalized for r in records]),
        "median_gre_total": _median([r.gre_total for r in records]),
        "median_gre_quant": _median([r.gre_quant for r in records]),
        "median_gre_verbal": _median([r.gre_verbal for r in records]),
        "median_toefl": _median([r.toefl for r in records]),
        "median_ielts": _median([r.ielts for r in records]),
        "research_percentage": _percentage_true([r.research_experience for r in records]),
        "median_publication_count": _median([r.publication_count for r in records]),
        "median_work_experience_months": _median([r.work_experience_months for r in records]),
    }


def get_program_statistics(db: Session, canonical_university: str, canonical_program: str) -> dict:
    records = get_historical_applications(db, canonical_university, canonical_program)
    admitted = [r for r in records if r.decision == "admitted"]
    rejected = [r for r in records if r.decision == "rejected"]
    waitlisted = [r for r in records if r.decision == "waitlisted"]
    years = [r.application_year for r in records if r.application_year is not None]
    return {"canonical_university": canonical_university, "canonical_program": canonical_program,
            "total_sample_size": len(records),
            "year_range": {"earliest": min(years) if years else None, "latest": max(years) if years else None},
            "admitted": _cohort_statistics(admitted), "rejected": _cohort_statistics(rejected),
            "waitlisted": _cohort_statistics(waitlisted)}
