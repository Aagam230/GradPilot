from typing import Optional


def calculate_sample_reliability(sample_size: int, median_similarity: Optional[float], recent_record_ratio: Optional[float] = None,
                                 average_data_quality: Optional[float] = None) -> dict:
    score = 0.0
    score += 40 if sample_size >= 100 else 35 if sample_size >= 50 else 30 if sample_size >= 25 else 22 if sample_size >= 15 else 15 if sample_size >= 10 else 8 if sample_size >= 5 else 0
    if median_similarity is not None:
        score += 30 if median_similarity >= .90 else 25 if median_similarity >= .80 else 18 if median_similarity >= .70 else 10 if median_similarity >= .60 else 3
    if recent_record_ratio is not None:
        score += 15 if recent_record_ratio >= .80 else 12 if recent_record_ratio >= .60 else 8 if recent_record_ratio >= .40 else 4 if recent_record_ratio >= .20 else 0
    if average_data_quality is not None:
        score += 15 if average_data_quality >= .90 else 12 if average_data_quality >= .75 else 8 if average_data_quality >= .60 else 4 if average_data_quality >= .40 else 0
    reliability = "Very Low" if sample_size < 5 else "High" if score >= 80 else "Moderate" if score >= 55 else "Low" if score >= 30 else "Very Low"
    return {"score": round(score,1), "reliability": reliability, "sample_size": sample_size, "median_similarity": median_similarity,
            "recent_record_ratio": recent_record_ratio, "average_data_quality": average_data_quality}


def build_historical_evidence(similarity_summary: dict, recent_record_ratio: Optional[float] = None,
                              average_data_quality: Optional[float] = None) -> dict:
    sample_size = similarity_summary.get("sample_size", 0)
    reliability = calculate_sample_reliability(sample_size, similarity_summary.get("median_similarity"), recent_record_ratio, average_data_quality)
    raw_signal = similarity_summary.get("historical_signal", "unavailable")
    return {"historical_signal": "unavailable" if sample_size < 5 else raw_signal, "raw_historical_signal": raw_signal,
            "reliability": reliability["reliability"], "reliability_score": reliability["score"], "sample_size": sample_size,
            "median_similarity": similarity_summary.get("median_similarity"), "outcome_distribution": similarity_summary.get("outcome_distribution", {}),
            "warning": "Historical outcomes are self-reported observational evidence and must not be interpreted as an admission probability."}
