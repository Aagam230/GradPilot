from unittest.mock import patch
from tests.conftest import fake_profile_extraction, fake_embed_texts

NO_SELECTIVITY_REQS = {
    "minimum_gpa": 3.0, "gre_required": False, "gre_minimum": None, "toefl_minimum": None,
    "ielts_minimum": None, "required_background": [], "required_prerequisites": [],
    "work_experience_required": None, "work_experience_preferred": None,
    "research_expectations": None, "selectivity_evidence": [], "sources": {},
}
HARD_FAIL_REQS = {
    "minimum_gpa": 3.0, "gre_required": True, "gre_minimum": 320, "toefl_minimum": None,
    "ielts_minimum": None, "required_background": [], "required_prerequisites": [],
    "work_experience_required": None, "work_experience_preferred": None,
    "research_expectations": None, "selectivity_evidence": [], "sources": {},
}


def _fake_hedging_analysis(system, user, max_tokens=2000, **kw):
    """A model that always hedges to 'Target' regardless of program -- this is the exact bug
    behavior the deterministic guardrails in analysis.py exist to catch."""
    return {
        "overall_fit_summary": "Reasonable fit.",
        "overall_classification": "Target",
        "confidence": "High",
        "classification_reasoning": "Meets general prerequisites.",
        "applicant_strength": {"rating": "Strong", "analysis": "Good GPA."},
        "program_competitiveness": {"rating": "Moderate", "analysis": "Unclear.", "evidence": []},
        "academic_fit": {"rating": "Strong", "analysis": "Good GPA.", "evidence": [1]},
        "research_fit": {"rating": "Moderate", "analysis": "Limited.", "evidence": []},
        "project_fit": {"rating": "Moderate", "analysis": "Some.", "evidence": []},
        "experience_fit": {"rating": "Moderate", "analysis": "Some.", "evidence": []},
        "program_alignment": {"rating": "Strong", "analysis": "Aligned.", "evidence": [1]},
        "strengths": ["GPA"], "weaknesses": [], "profile_gaps": [], "recommended_improvements": [],
    }


def _run_analysis(client, university, program, manual_text):
    r = client.post("/api/profile/upload", files={"file": ("cv.pdf", _sample_cv(), "application/pdf")}, data={"doc_type": "cv"})
    profile_id = r.json()["profile_id"]
    r = client.post("/api/program/retrieve", json={
        "university_name": university, "program_name": program, "manual_text": manual_text,
    })
    program_id = r.json()["program_id"]
    r = client.post("/api/analysis", json={"profile_id": profile_id, "program_id": program_id})
    return r.json()["result"]


def _sample_cv():
    from reportlab.pdfgen import canvas
    import io
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    for i, line in enumerate([
        "Jane Doe", "Education: BSc CS, MIT, GPA 3.6, 2020-2024", "Test Scores: GRE 314",
    ]):
        c.drawString(50, 800 - i * 20, line)
    c.save()
    return buf.getvalue()


def _patched(requirements_by_call):
    """requirements_by_call: fn(chunks) -> dict, so different programs can return different reqs."""
    return patch("app.services.requirement_extraction.extract_requirements", side_effect=requirements_by_call)


def test_same_applicant_no_selectivity_data_gives_consistent_result(client):
    with patch("app.services.profile_extraction.generate_json", return_value=fake_profile_extraction()), \
         patch("app.services.analysis.generate_json", side_effect=_fake_hedging_analysis), \
         patch("app.services.program_resolution.resolve_program", side_effect=lambda u, p: {
             "canonical_university": u, "canonical_program": p, "official_domain": None}), \
         patch("app.services.requirement_extraction.extract_requirements", return_value=dict(NO_SELECTIVITY_REQS)), \
         patch("app.services.community_outcomes.search_community_outcome_pages", return_value=[]), \
         patch("app.services.rag.embed_texts", side_effect=fake_embed_texts), \
         patch("app.services.rag.embed_text", side_effect=lambda t: fake_embed_texts([t])[0]):

        asu_result = _run_analysis(client, "ASU", "MS Computer Science", "Bachelor's degree required. Minimum GPA 3.0.")
        nus_result = _run_analysis(client, "NUS", "Master of Computing", "Bachelor's degree required. Minimum GPA 3.0.")

    # This is the exact bug reported: same applicant, no real selectivity evidence for either
    # program, yet the model wanted to say Reach for one and Target for the other.
    assert asu_result["overall_classification"] == "Insufficient Evidence"
    assert nus_result["overall_classification"] == "Insufficient Evidence"
    assert asu_result["overall_classification"] == nus_result["overall_classification"]
    assert asu_result["confidence"] == "Low"


def test_hard_requirement_failure_floors_classification_at_reach(client):
    with patch("app.services.profile_extraction.generate_json", return_value=fake_profile_extraction()), \
         patch("app.services.analysis.generate_json", side_effect=_fake_hedging_analysis), \
         patch("app.services.program_resolution.resolve_program", side_effect=lambda u, p: {
             "canonical_university": u, "canonical_program": p, "official_domain": None}), \
         patch("app.services.requirement_extraction.extract_requirements", return_value=dict(HARD_FAIL_REQS)), \
         patch("app.services.community_outcomes.search_community_outcome_pages", return_value=[]), \
         patch("app.services.rag.embed_texts", side_effect=fake_embed_texts), \
         patch("app.services.rag.embed_text", side_effect=lambda t: fake_embed_texts([t])[0]):

        result = _run_analysis(client, "Stanford", "MS Computer Science", "GRE required, minimum 320.")

    # Applicant's GRE is 314 (see fake_profile_extraction default) -- below the stated 320 minimum.
    # The mocked LLM said "Target"; the guardrail must override it regardless.
    assert result["overall_classification"] in ("Reach", "Very High Reach")
    gre_check = next(c for c in result["requirement_check"]["checks"] if c["requirement"] == "Minimum GRE")
    assert gre_check["meets"] is False


def test_full_official_selectivity_evidence_allows_confident_classification(client):
    strong_reqs = dict(NO_SELECTIVITY_REQS)
    strong_reqs["selectivity_evidence"] = ["Highly selective, ~15% acceptance rate"]
    # Substantive enough evidence text to produce 2+ chunks -- isolates what's under test
    # (presence of real selectivity data) from the separate "thin evidence" confidence cap.
    substantive_text = (
        "This program is highly selective, admitting approximately 15% of applicants each year. "
        "Admitted students typically have a strong academic record and relevant research or "
        "industry experience. The typical incoming cohort has an average undergraduate GPA of "
        "3.7 and includes students from a wide range of quantitative backgrounds."
    )

    with patch("app.services.profile_extraction.generate_json", return_value=fake_profile_extraction()), \
         patch("app.services.analysis.generate_json", side_effect=_fake_hedging_analysis), \
         patch("app.services.program_resolution.resolve_program", side_effect=lambda u, p: {
             "canonical_university": u, "canonical_program": p, "official_domain": None}), \
         patch("app.services.requirement_extraction.extract_requirements", return_value=strong_reqs), \
         patch("app.services.community_outcomes.search_community_outcome_pages", return_value=[]), \
         patch("app.services.rag.embed_texts", side_effect=fake_embed_texts), \
         patch("app.services.rag.embed_text", side_effect=lambda t: fake_embed_texts([t])[0]):

        result = _run_analysis(client, "Some University", "MS Data Science", substantive_text)

    assert result["overall_classification"] == "Target"  # the LLM's own (non-hedged, evidence-backed) call stands
    assert result["confidence"] == "High"  # real selectivity data + substantive evidence allows full confidence
