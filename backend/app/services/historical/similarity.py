from typing import Optional

from sqlalchemy.orm import Session

from .repository import get_historical_applications


# Relative importance of each feature.
# These are heuristic weights, NOT learned admission weights.
FEATURE_WEIGHTS = {
    "gpa_normalized": 0.30,
    "gre_total": 0.20,
    "gre_quant": 0.10,
    "toefl": 0.05,
    "research_experience": 0.15,
    "publication_count": 0.10,
    "work_experience_months": 0.10,
}


def _numeric_similarity(
    applicant_value: Optional[float],
    historical_value: Optional[float],
    value_range: float,
) -> Optional[float]:
    """
    Return similarity between 0 and 1.

    Missing values return None and therefore do not penalize either
    applicant.
    """

    if applicant_value is None or historical_value is None:
        return None

    difference = abs(applicant_value - historical_value)

    similarity = 1 - (difference / value_range)

    return max(0.0, min(1.0, similarity))


def _boolean_similarity(
    applicant_value: Optional[bool],
    historical_value: Optional[bool],
) -> Optional[float]:

    if applicant_value is None or historical_value is None:
        return None

    return 1.0 if applicant_value == historical_value else 0.0


def calculate_similarity(
    applicant: dict,
    historical,
) -> dict:
    """
    Calculate weighted similarity between the current applicant and
    one historical applicant.

    Only features known for BOTH applicants contribute to the score.
    """

    comparisons = {
        "gpa_normalized": _numeric_similarity(
            applicant.get("gpa_normalized"),
            historical.gpa_normalized,
            1.0,
        ),

        "gre_total": _numeric_similarity(
            applicant.get("gre_total"),
            historical.gre_total,
            80.0,
        ),

        "gre_quant": _numeric_similarity(
            applicant.get("gre_quant"),
            historical.gre_quant,
            40.0,
        ),

        "toefl": _numeric_similarity(
            applicant.get("toefl"),
            historical.toefl,
            120.0,
        ),

        "research_experience": _boolean_similarity(
            applicant.get("research_experience"),
            historical.research_experience,
        ),

        "publication_count": _numeric_similarity(
            applicant.get("publication_count"),
            historical.publication_count,
            5.0,
        ),

        "work_experience_months": _numeric_similarity(
            applicant.get("work_experience_months"),
            historical.work_experience_months,
            60.0,
        ),
    }

    weighted_sum = 0.0
    used_weight = 0.0

    for feature, similarity in comparisons.items():

        if similarity is None:
            continue

        weight = FEATURE_WEIGHTS[feature]

        weighted_sum += similarity * weight
        used_weight += weight

    if used_weight == 0:
        overall_similarity = None
    else:
        overall_similarity = weighted_sum / used_weight

    return {
        "historical_application_id": str(historical.id),
        "decision": historical.decision,
        "application_year": historical.application_year,

        "similarity": (
            round(overall_similarity, 4)
            if overall_similarity is not None
            else None
        ),

        "feature_coverage": round(used_weight, 3),

        "feature_similarities": {
            key: (
                round(value, 4)
                if value is not None
                else None
            )
            for key, value in comparisons.items()
        },
    }


def find_similar_applicants(
    db: Session,
    canonical_university: str,
    canonical_program: str,
    applicant: dict,
    limit: int = 20,
    minimum_coverage: float = 0.40,
) -> list[dict]:
    """
    Retrieve historical applicants for the canonical program and
    rank them by similarity to the current applicant.
    """

    records = get_historical_applications(
        db=db,
        canonical_university=canonical_university,
        canonical_program=canonical_program,
    )

    results = []

    for record in records:

        comparison = calculate_similarity(
            applicant=applicant,
            historical=record,
        )

        if comparison["similarity"] is None:
            continue

        if comparison["feature_coverage"] < minimum_coverage:
            continue

        results.append(comparison)

    results.sort(
        key=lambda item: item["similarity"],
        reverse=True,
    )

    return results[:limit]


def summarize_similar_applicants(
    similar_applicants: list[dict],
) -> dict:
    """
    Summarize outcomes among the nearest historical applicants.

    The outcome distribution is an evidence signal, NOT an admission
    probability.
    """

    if not similar_applicants:
        return {
            "sample_size": 0,
            "admitted": 0,
            "rejected": 0,
            "waitlisted": 0,
            "median_similarity": None,
            "historical_signal": "unavailable",
        }

    admitted = sum(
        1
        for applicant in similar_applicants
        if applicant["decision"] == "admitted"
    )

    rejected = sum(
        1
        for applicant in similar_applicants
        if applicant["decision"] == "rejected"
    )

    waitlisted = sum(
        1
        for applicant in similar_applicants
        if applicant["decision"] == "waitlisted"
    )

    similarities = sorted(
        applicant["similarity"]
        for applicant in similar_applicants
        if applicant["similarity"] is not None
    )

    midpoint = len(similarities) // 2

    if len(similarities) % 2:
        median_similarity = similarities[midpoint]
    else:
        median_similarity = (
            similarities[midpoint - 1]
            + similarities[midpoint]
        ) / 2

    decided = admitted + rejected

    if decided < 5:
        signal = "insufficient_sample"

    else:
        admitted_share = admitted / decided

        if admitted_share >= 0.75:
            signal = "strongly_favourable"

        elif admitted_share >= 0.60:
            signal = "favourable"

        elif admitted_share >= 0.40:
            signal = "mixed"

        elif admitted_share >= 0.25:
            signal = "unfavourable"

        else:
            signal = "strongly_unfavourable"

    return {
        "sample_size": len(similar_applicants),
        "admitted": admitted,
        "rejected": rejected,
        "waitlisted": waitlisted,

        "median_similarity": round(
            median_similarity,
            4,
        ),

        "historical_signal": signal,

        # Explicitly NOT an admission probability.
        "outcome_distribution": {
            "admitted": admitted,
            "rejected": rejected,
            "waitlisted": waitlisted,
        },
    }