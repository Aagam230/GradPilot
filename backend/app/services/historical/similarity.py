from typing import Optional
from sqlalchemy.orm import Session
from .repository import get_historical_applications

FEATURE_WEIGHTS = {"gpa_normalized": 0.30, "gre_total": 0.20, "gre_quant": 0.10, "toefl": 0.05,
                   "research_experience": 0.15, "publication_count": 0.10, "work_experience_months": 0.10}


def _numeric_similarity(a: Optional[float], h: Optional[float], value_range: float) -> Optional[float]:
    if a is None or h is None: return None
    return max(0.0, min(1.0, 1 - abs(a - h) / value_range))


def _boolean_similarity(a: Optional[bool], h: Optional[bool]) -> Optional[float]:
    if a is None or h is None: return None
    return 1.0 if a == h else 0.0


def calculate_similarity(applicant: dict, historical) -> dict:
    comparisons = {
        "gpa_normalized": _numeric_similarity(applicant.get("gpa_normalized"), historical.gpa_normalized, 1.0),
        "gre_total": _numeric_similarity(applicant.get("gre_total"), historical.gre_total, 80.0),
        "gre_quant": _numeric_similarity(applicant.get("gre_quant"), historical.gre_quant, 40.0),
        "toefl": _numeric_similarity(applicant.get("toefl"), historical.toefl, 120.0),
        "research_experience": _boolean_similarity(applicant.get("research_experience"), historical.research_experience),
        "publication_count": _numeric_similarity(applicant.get("publication_count"), historical.publication_count, 5.0),
        "work_experience_months": _numeric_similarity(applicant.get("work_experience_months"), historical.work_experience_months, 60.0),
    }
    weighted_sum = used_weight = 0.0
    for feature, similarity in comparisons.items():
        if similarity is None: continue
        weight = FEATURE_WEIGHTS[feature]; weighted_sum += similarity * weight; used_weight += weight
    overall = weighted_sum / used_weight if used_weight else None
    return {"historical_application_id": str(historical.id), "decision": historical.decision,
            "application_year": historical.application_year, "similarity": round(overall, 4) if overall is not None else None,
            "feature_coverage": round(used_weight, 3),
            "feature_similarities": {k: round(v, 4) if v is not None else None for k, v in comparisons.items()}}


def find_similar_applicants(db: Session, canonical_university: str, canonical_program: str, applicant: dict,
                            limit: int = 20, minimum_coverage: float = 0.40) -> list[dict]:
    results = []
    for record in get_historical_applications(db, canonical_university, canonical_program):
        comparison = calculate_similarity(applicant, record)
        if comparison["similarity"] is not None and comparison["feature_coverage"] >= minimum_coverage:
            results.append(comparison)
    results.sort(key=lambda item: item["similarity"], reverse=True)
    return results[:limit]


def summarize_similar_applicants(items: list[dict]) -> dict:
    if not items:
        return {"sample_size": 0, "admitted": 0, "rejected": 0, "waitlisted": 0, "median_similarity": None, "historical_signal": "unavailable"}
    admitted = sum(x["decision"] == "admitted" for x in items); rejected = sum(x["decision"] == "rejected" for x in items)
    waitlisted = sum(x["decision"] == "waitlisted" for x in items)
    sims = sorted(x["similarity"] for x in items if x["similarity"] is not None); mid = len(sims)//2
    med = sims[mid] if len(sims)%2 else (sims[mid-1]+sims[mid])/2
    decided = admitted + rejected
    if decided < 5: signal = "insufficient_sample"
    else:
        share = admitted / decided
        signal = "strongly_favourable" if share >= .75 else "favourable" if share >= .60 else "mixed" if share >= .40 else "unfavourable" if share >= .25 else "strongly_unfavourable"
    return {"sample_size": len(items), "admitted": admitted, "rejected": rejected, "waitlisted": waitlisted,
            "median_similarity": round(med,4), "historical_signal": signal,
            "outcome_distribution": {"admitted": admitted, "rejected": rejected, "waitlisted": waitlisted}}
