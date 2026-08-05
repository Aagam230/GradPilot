from statistics import median
from typing import Optional

from sqlalchemy.orm import Session

from .repository import get_historical_applications


def _median(values: list) -> Optional[float]:
    clean = [value for value in values if value is not None]

    if not clean:
        return None

    return round(float(median(clean)), 3)


def _percentage_true(values: list) -> Optional[float]:
    """
    Calculate percentage of known boolean values that are True.

    Unknown/None values are excluded rather than treated as False.
    """
    known = [value for value in values if value is not None]

    if not known:
        return None

    return round(
        (sum(1 for value in known if value) / len(known)) * 100,
        1,
    )


def _cohort_statistics(records: list) -> dict:
    """
    Calculate descriptive statistics for a historical applicant cohort.
    """

    if not records:
        return {
            "sample_size": 0,
            "median_gpa_normalized": None,
            "median_gre_total": None,
            "median_gre_quant": None,
            "median_gre_verbal": None,
            "median_toefl": None,
            "median_ielts": None,
            "research_percentage": None,
            "median_publication_count": None,
            "median_work_experience_months": None,
        }

    return {
        "sample_size": len(records),

        "median_gpa_normalized": _median(
            [r.gpa_normalized for r in records]
        ),

        "median_gre_total": _median(
            [r.gre_total for r in records]
        ),

        "median_gre_quant": _median(
            [r.gre_quant for r in records]
        ),

        "median_gre_verbal": _median(
            [r.gre_verbal for r in records]
        ),

        "median_toefl": _median(
            [r.toefl for r in records]
        ),

        "median_ielts": _median(
            [r.ielts for r in records]
        ),

        "research_percentage": _percentage_true(
            [r.research_experience for r in records]
        ),

        "median_publication_count": _median(
            [r.publication_count for r in records]
        ),

        "median_work_experience_months": _median(
            [r.work_experience_months for r in records]
        ),
    }


def get_program_statistics(
    db: Session,
    canonical_university: str,
    canonical_program: str,
) -> dict:
    """
    Compare admitted, rejected, and waitlisted historical cohorts
    for one canonical program.
    """

    records = get_historical_applications(
        db=db,
        canonical_university=canonical_university,
        canonical_program=canonical_program,
    )

    admitted = [
        record
        for record in records
        if record.decision == "admitted"
    ]

    rejected = [
        record
        for record in records
        if record.decision == "rejected"
    ]

    waitlisted = [
        record
        for record in records
        if record.decision == "waitlisted"
    ]

    years = [
        record.application_year
        for record in records
        if record.application_year is not None
    ]

    return {
        "canonical_university": canonical_university,
        "canonical_program": canonical_program,

        "total_sample_size": len(records),

        "year_range": {
            "earliest": min(years) if years else None,
            "latest": max(years) if years else None,
        },

        "admitted": _cohort_statistics(admitted),
        "rejected": _cohort_statistics(rejected),
        "waitlisted": _cohort_statistics(waitlisted),
    }