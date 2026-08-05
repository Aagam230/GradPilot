from typing import Optional


def calculate_sample_reliability(
    sample_size: int,
    median_similarity: Optional[float],
    recent_record_ratio: Optional[float] = None,
    average_data_quality: Optional[float] = None,
) -> dict:
    """
    Estimate how much trust GradPilot should place in historical evidence.

    This is NOT a measure of admission probability.

    Reliability depends on:
    - number of comparable historical applicants
    - similarity of those applicants
    - recency of records, when available
    - data quality, when available
    """

    score = 0.0

    # ---------------------------------------------------------
    # 1. Sample size — maximum 40 points
    # ---------------------------------------------------------

    if sample_size >= 100:
        score += 40

    elif sample_size >= 50:
        score += 35

    elif sample_size >= 25:
        score += 30

    elif sample_size >= 15:
        score += 22

    elif sample_size >= 10:
        score += 15

    elif sample_size >= 5:
        score += 8

    # ---------------------------------------------------------
    # 2. Similarity quality — maximum 30 points
    # ---------------------------------------------------------

    if median_similarity is not None:

        if median_similarity >= 0.90:
            score += 30

        elif median_similarity >= 0.80:
            score += 25

        elif median_similarity >= 0.70:
            score += 18

        elif median_similarity >= 0.60:
            score += 10

        else:
            score += 3

    # ---------------------------------------------------------
    # 3. Recency — maximum 15 points
    # ---------------------------------------------------------

    if recent_record_ratio is not None:

        if recent_record_ratio >= 0.80:
            score += 15

        elif recent_record_ratio >= 0.60:
            score += 12

        elif recent_record_ratio >= 0.40:
            score += 8

        elif recent_record_ratio >= 0.20:
            score += 4

    # ---------------------------------------------------------
    # 4. Data quality — maximum 15 points
    # ---------------------------------------------------------

    if average_data_quality is not None:

        if average_data_quality >= 0.90:
            score += 15

        elif average_data_quality >= 0.75:
            score += 12

        elif average_data_quality >= 0.60:
            score += 8

        elif average_data_quality >= 0.40:
            score += 4

    # ---------------------------------------------------------
    # Reliability classification
    # ---------------------------------------------------------

    if sample_size < 5:
        reliability = "Very Low"

    elif score >= 80:
        reliability = "High"

    elif score >= 55:
        reliability = "Moderate"

    elif score >= 30:
        reliability = "Low"

    else:
        reliability = "Very Low"

    return {
        "score": round(score, 1),
        "reliability": reliability,
        "sample_size": sample_size,
        "median_similarity": median_similarity,
        "recent_record_ratio": recent_record_ratio,
        "average_data_quality": average_data_quality,
    }


def build_historical_evidence(
    similarity_summary: dict,
    recent_record_ratio: Optional[float] = None,
    average_data_quality: Optional[float] = None,
) -> dict:
    """
    Convert nearest-neighbour results into an evidence object that can
    eventually be consumed by GradPilot's admission classifier.
    """

    sample_size = similarity_summary.get("sample_size", 0)

    reliability = calculate_sample_reliability(
        sample_size=sample_size,
        median_similarity=similarity_summary.get(
            "median_similarity"
        ),
        recent_record_ratio=recent_record_ratio,
        average_data_quality=average_data_quality,
    )

    raw_signal = similarity_summary.get(
        "historical_signal",
        "unavailable",
    )

    # Tiny samples should never provide meaningful admission evidence.
    if sample_size < 5:
        usable_signal = "unavailable"

    else:
        usable_signal = raw_signal

    return {
        "historical_signal": usable_signal,

        "raw_historical_signal": raw_signal,

        "reliability": reliability["reliability"],

        "reliability_score": reliability["score"],

        "sample_size": sample_size,

        "median_similarity": similarity_summary.get(
            "median_similarity"
        ),

        "outcome_distribution": similarity_summary.get(
            "outcome_distribution",
            {},
        ),

        "warning": (
            "Historical outcomes are self-reported observational "
            "evidence and must not be interpreted as an admission "
            "probability."
        ),
    }