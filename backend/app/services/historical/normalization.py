from typing import Optional


def normalize_gpa(gpa_value: Optional[float], gpa_scale: Optional[float]) -> Optional[float]:
    if gpa_value is None or gpa_scale is None or gpa_scale <= 0:
        return None
    normalized = gpa_value / gpa_scale
    if normalized < 0 or normalized > 1:
        return None
    return round(normalized, 4)


def normalize_decision(decision: Optional[str]) -> Optional[str]:
    if not decision:
        return None
    value = decision.strip().lower()
    if value in {"admit", "admitted", "accepted", "accept", "offer", "offered"}:
        return "admitted"
    if value in {"reject", "rejected", "denied", "declined"}:
        return "rejected"
    if value in {"waitlist", "waitlisted", "wait list"}:
        return "waitlisted"
    return None


def normalize_gre(gre_total: Optional[int], gre_quant: Optional[int] = None, gre_verbal: Optional[int] = None) -> dict:
    result = {"gre_total": None, "gre_quant": None, "gre_verbal": None}
    if gre_quant is not None and 130 <= gre_quant <= 170:
        result["gre_quant"] = gre_quant
    if gre_verbal is not None and 130 <= gre_verbal <= 170:
        result["gre_verbal"] = gre_verbal
    if gre_total is not None and 260 <= gre_total <= 340:
        result["gre_total"] = gre_total
    if result["gre_total"] is None and result["gre_quant"] is not None and result["gre_verbal"] is not None:
        result["gre_total"] = result["gre_quant"] + result["gre_verbal"]
    return result


def normalize_toefl(score: Optional[int]) -> Optional[int]:
    return score if score is not None and 0 <= score <= 120 else None


def normalize_ielts(score: Optional[float]) -> Optional[float]:
    return round(score, 1) if score is not None and 0 <= score <= 9 else None


def normalize_boolean(value) -> Optional[bool]:
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
    gre = normalize_gre(record.get("gre_total"), record.get("gre_quant"), record.get("gre_verbal"))
    gpa_value, gpa_scale = record.get("gpa_value"), record.get("gpa_scale")
    return {
        "canonical_university": record.get("canonical_university"),
        "canonical_program": record.get("canonical_program"),
        "application_year": record.get("application_year"),
        "decision": normalize_decision(record.get("decision")),
        "gpa_value": gpa_value,
        "gpa_scale": gpa_scale,
        "gpa_normalized": normalize_gpa(gpa_value, gpa_scale),
        "gre_total": gre["gre_total"], "gre_quant": gre["gre_quant"], "gre_verbal": gre["gre_verbal"],
        "toefl": normalize_toefl(record.get("toefl")),
        "ielts": normalize_ielts(record.get("ielts")),
        "undergraduate_major": record.get("undergraduate_major"),
        "undergraduate_country": record.get("undergraduate_country"),
        "research_experience": normalize_boolean(record.get("research_experience")),
        "publication_count": record.get("publication_count"),
        "work_experience_months": record.get("work_experience_months"),
        "source_type": record.get("source_type", "manual"),
        "source_url": record.get("source_url"),
        "data_quality_score": record.get("data_quality_score"),
    }
