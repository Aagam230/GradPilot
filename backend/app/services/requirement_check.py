"""Deterministic comparison of the applicant's structured profile against a program's structured
requirements. Numeric comparisons (e.g. applicant GRE 314 vs stated minimum 320) are computed
here in code, not left to the LLM to eyeball and potentially get wrong or ignore.
"""
import re


def _first_number(text: str) -> float | None:
    m = re.search(r"(\d+(?:\.\d+)?)", str(text or ""))
    return float(m.group(1)) if m else None


def _extract_test_score(profile: dict, test_keyword: str) -> float | None:
    for t in profile.get("test_scores", []) or []:
        if test_keyword in (t.get("test") or "").lower():
            score = _first_number(t.get("score"))
            if score is not None:
                return score
    return None


def _extract_gpa(profile: dict) -> float | None:
    for e in profile.get("education", []) or []:
        gpa = _first_number(e.get("gpa"))
        if gpa is not None:
            return gpa
    return None


def check_requirements(profile: dict, requirements: dict) -> dict:
    """Returns individual pass/fail checks plus aggregate flags used to deterministically bound
    the LLM's classification (see analysis.py)."""
    requirements = requirements or {}
    checks = []
    any_failure = False
    any_unknown_applicant_value = False

    def add_check(label: str, required, applicant_value, meets):
        nonlocal any_failure, any_unknown_applicant_value
        if meets is None:
            any_unknown_applicant_value = True
        elif meets is False:
            any_failure = True
        checks.append({
            "requirement": label,
            "required": required,
            "applicant_value": applicant_value,
            "meets": meets,
        })

    min_gpa = requirements.get("minimum_gpa")
    if min_gpa is not None:
        applicant_gpa = _extract_gpa(profile)
        meets = (applicant_gpa >= min_gpa) if applicant_gpa is not None else None
        add_check("Minimum GPA", min_gpa, applicant_gpa, meets)

    gre_min = requirements.get("gre_minimum")
    if gre_min is not None:
        applicant_gre = _extract_test_score(profile, "gre")
        meets = (applicant_gre >= gre_min) if applicant_gre is not None else None
        add_check("Minimum GRE", gre_min, applicant_gre, meets)

    toefl_min = requirements.get("toefl_minimum")
    if toefl_min is not None:
        applicant_toefl = _extract_test_score(profile, "toefl")
        meets = (applicant_toefl >= toefl_min) if applicant_toefl is not None else None
        add_check("Minimum TOEFL", toefl_min, applicant_toefl, meets)

    ielts_min = requirements.get("ielts_minimum")
    if ielts_min is not None:
        applicant_ielts = _extract_test_score(profile, "ielts")
        meets = (applicant_ielts >= ielts_min) if applicant_ielts is not None else None
        add_check("Minimum IELTS", ielts_min, applicant_ielts, meets)

    return {
        "checks": checks,
        "any_hard_failure": any_failure,
        "any_unknown_applicant_value": any_unknown_applicant_value,
        "has_selectivity_evidence": bool(requirements.get("selectivity_evidence")),
    }
