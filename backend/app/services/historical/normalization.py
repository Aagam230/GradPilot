from typing import Optional


def normalize_gpa(
    gpa_value: Optional[float],
    gpa_scale: Optional[float],
) -> Optional[float]:
    """
    Normalize GPA to a 0-1 range.

    This is NOT intended to claim equivalence between different
    international grading systems. It provides a common numerical
    representation for historical similarity calculations.
    """
    if gpa_value is None or gpa_scale is None:
        return None

    if gpa_scale <= 0:
        return None

    normalized = gpa_value / gpa_scale

    if normalized < 0 or normalized > 1:
        return None

    return round(normalized, 4)


def normalize_decision(decision: Optional[str]) -> Optional[str]:
    """
    Convert common decision labels into canonical values.
    """
    if not decision:
        return None

    value = decision.strip().lower()

    admitted_aliases = {
        "admit",
        "admitted",
        "accepted",
        "accept",
        "offer",
        "offered",
    }

    rejected_aliases = {
        "reject",
        "rejected",
        "denied",
        "declined",
    }

    waitlisted_aliases = {
        "waitlist",
        "waitlisted",
        "wait list",
    }

    if value in admitted_aliases:
        return "admitted"

    if value in rejected_aliases:
        return "rejected"

    if value in waitlisted_aliases:
        return "waitlisted"

    return None


def normalize_gre(
    gre_total: Optional[int],
    gre_quant: Optional[int] = None,
    gre_verbal: Optional[int] = None,
) -> dict:
    """
    Normalize and validate GRE scores.

    Current GRE:
    Quantitative: 130-170
    Verbal:       130-170
    Total:        260-340
    """

    result = {
        "gre_total": None,
        "gre_quant": None,
        "gre_verbal": None,
    }

    if gre_quant is not None and 130 <= gre_quant <= 170:
        result["gre_quant"] = gre_quant

    if gre_verbal is not None and 130 <= gre_verbal <= 170:
        result["gre_verbal"] = gre_verbal

    if gre_total is not None and 260 <= gre_total <= 340:
        result["gre_total"] = gre_total

    # Calculate total if components exist but total does not.
    if (
        result["gre_total"] is None
        and result["gre_quant"] is not None
        and result["gre_verbal"] is not None
    ):
        result["gre_total"] = (
            result["gre_quant"] + result["gre_verbal"]
        )

    return result


def normalize_toefl(score: Optional[int]) -> Optional[int]:
    if score is None:
        return None

    if 0 <= score <= 120:
        return score

    return None


def normalize_ielts(score: Optional[float]) -> Optional[float]:
    if score is None:
        return None

    if 0 <= score <= 9:
        return round(score, 1)

    return None


def normalize_boolean(value) -> Optional[bool]:
    """
    Normalize common boolean representations from imported datasets.
    """
    if value is None:
        return None

    if isinstance(value, bool):
        return value

    text = str(value).strip().lower()

    if text in {"yes", "true", "1", "y"}:
        return True

    if text in {"no", "false", "0", "n"}:
        return False

    return None


def normalize_application_record(record: dict) -> dict:
    """
    Normalize one historical application record before storage.
    """

    gre = normalize_gre(
        record.get("gre_total"),
        record.get("gre_quant"),
        record.get("gre_verbal"),
    )

    gpa_value = record.get("gpa_value")
    gpa_scale = record.get("gpa_scale")

    return {
        "canonical_university": record.get("canonical_university"),
        "canonical_program": record.get("canonical_program"),

        "application_year": record.get("application_year"),
        "decision": normalize_decision(record.get("decision")),

        "gpa_value": gpa_value,
        "gpa_scale": gpa_scale,
        "gpa_normalized": normalize_gpa(
            gpa_value,
            gpa_scale,
        ),

        "gre_total": gre["gre_total"],
        "gre_quant": gre["gre_quant"],
        "gre_verbal": gre["gre_verbal"],

        "toefl": normalize_toefl(record.get("toefl")),
        "ielts": normalize_ielts(record.get("ielts")),

        "undergraduate_major": record.get("undergraduate_major"),
        "undergraduate_country": record.get("undergraduate_country"),

        "research_experience": normalize_boolean(
            record.get("research_experience")
        ),

        "publication_count": record.get("publication_count"),
        "work_experience_months": record.get(
            "work_experience_months"
        ),

        "source_type": record.get("source_type", "manual"),
        "source_url": record.get("source_url"),
        "data_quality_score": record.get("data_quality_score"),
    }