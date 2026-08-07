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
FAKE_OUTCOMES = [
    {"summary": "Reported accepted; GPA 3.7, GRE 322 (self-reported, unverified).", "decision": "accepted", "source_url": "https://thegradcafe.com/x"},
    {"summary": "Reported rejected; GPA 3.4, GRE 310 (self-reported, unverified).", "decision": "rejected", "source_url": "https://thegradcafe.com/x"},
    {"summary": "Reported accepted; GPA 3.9 (self-reported, unverified).", "decision": "accepted", "source_url": "https://reddit.com/x"},
]


def _resolve_passthrough(university_name, program_name):
    return {"canonical_university": university_name, "canonical_program": program_name, "official_domain": None}


def _fake_hedged_target(system, user, max_tokens=2000, **kw):
    return {
        "overall_fit_summary": "Reasonable fit.",
        "overall_classification": "Target",
        "confidence": "High",
        "classification_reasoning": "Meets general prerequisites.",
        "applicant_strength": {"rating": "Strong", "analysis": "Good GPA."},
        "program_competitiveness": {"rating": "Moderate", "analysis": "Some data.", "evidence": []},
        "academic_fit": {"rating": "Strong", "analysis": "Good.", "evidence": [1]},
        "research_fit": {"rating": "Moderate", "analysis": "Limited.", "evidence": []},
        "project_fit": {"rating": "Moderate", "analysis": "Some.", "evidence": []},
        "experience_fit": {"rating": "Moderate", "analysis": "Some.", "evidence": []},
        "program_alignment": {"rating": "Strong", "analysis": "Aligned.", "evidence": [1]},
        "strengths": ["GPA"], "weaknesses": [], "profile_gaps": [], "recommended_improvements": [],
    }


def _fake_incorrectly_likely_despite_failure(system, user, max_tokens=2000, **kw):
    result = _fake_hedged_target(system, user, max_tokens, **kw)
    result["overall_classification"] = "Likely"
    result["classification_reasoning"] = "Community reports suggest people with lower GRE got in."
    return result


def _upload_and_retrieve(client, university, program, manual_text):
    r = client.post("/api/profile/upload", files={"file": ("cv.pdf", _sample_cv(), "application/pdf")}, data={"doc_type": "cv"})
    profile_id = r.json()["profile_id"]
    r = client.post("/api/program/retrieve", json={
        "university_name": university, "program_name": program, "manual_text": manual_text,
    })
    return profile_id, r.json()["program_id"]


def _sample_cv():
    from reportlab.pdfgen import canvas
    import io
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    for i, line in enumerate(["Jane Doe", "Education: BSc CS, MIT, GPA 3.6, 2020-2024", "Test Scores: GRE 314"]):
        c.drawString(50, 800 - i * 20, line)
    c.save()
    return buf.getvalue()


def test_community_signal_unlocks_classification_with_capped_confidence(client):
    with patch("app.services.profile_extraction.generate_json", return_value=fake_profile_extraction()), \
         patch("app.services.analysis.generate_json", side_effect=_fake_hedged_target), \
         patch("app.services.program_resolution.resolve_program", side_effect=_resolve_passthrough), \
         patch("app.services.requirement_extraction.extract_requirements", return_value=dict(NO_SELECTIVITY_REQS)), \
         patch("app.services.community_outcomes.search_community_outcome_pages",
               return_value=[{"url": "https://thegradcafe.com/x", "title": "results"}]), \
         patch("app.services.web_search.fetch_page_text",
               return_value="Applicant A: Accepted GPA 3.7 GRE 322. Applicant B: Rejected GPA 3.4 GRE 310. Applicant C: Accepted GPA 3.9."), \
         patch("app.services.community_outcomes.extract_outcome_evidence", return_value=FAKE_OUTCOMES), \
         patch("app.services.rag.embed_texts", side_effect=fake_embed_texts), \
         patch("app.services.rag.embed_text", side_effect=lambda t: fake_embed_texts([t])[0]):

        profile_id, program_id = _upload_and_retrieve(client, "Small State University", "MS Data Science",
                                                        "Applicants need a bachelor's degree. Minimum GPA 3.0.")
        r = client.post("/api/analysis", json={"profile_id": profile_id, "program_id": program_id})

    result = r.json()["result"]
    assert result["overall_classification"] == "Target"  # allowed to stand
    assert result["confidence"] != "High"  # but never earns full confidence on community data alone
    assert len(result["community_outcome_evidence"]) == 3
    assert "self-reported" in result["classification_reasoning"].lower() or "unverified" in result["classification_reasoning"].lower()


def test_community_data_cannot_override_official_hard_requirement_failure(client):
    """The critical safety property of this whole tier: favorable self-reported outcomes must
    never excuse a failure against an OFFICIAL stated requirement."""
    with patch("app.services.profile_extraction.generate_json", return_value=fake_profile_extraction()), \
         patch("app.services.analysis.generate_json", side_effect=_fake_incorrectly_likely_despite_failure), \
         patch("app.services.program_resolution.resolve_program", side_effect=_resolve_passthrough), \
         patch("app.services.requirement_extraction.extract_requirements", return_value=dict(HARD_FAIL_REQS)), \
         patch("app.services.community_outcomes.search_community_outcome_pages",
               return_value=[{"url": "https://thegradcafe.com/x", "title": "results"}]), \
         patch("app.services.web_search.fetch_page_text",
               return_value="Several applicants reported acceptance with GRE scores below 320."), \
         patch("app.services.community_outcomes.extract_outcome_evidence", return_value=[
             {"summary": "Reported accepted; GRE 312 (self-reported, unverified).", "decision": "accepted", "source_url": "x"},
             {"summary": "Reported accepted; GRE 308 (self-reported, unverified).", "decision": "accepted", "source_url": "x"},
             {"summary": "Reported accepted; GRE 315 (self-reported, unverified).", "decision": "accepted", "source_url": "x"},
         ]), \
         patch("app.services.rag.embed_texts", side_effect=fake_embed_texts), \
         patch("app.services.rag.embed_text", side_effect=lambda t: fake_embed_texts([t])[0]):

        profile_id, program_id = _upload_and_retrieve(client, "Strict University", "MS Computer Science",
                                                        "GRE required, minimum 320.")
        r = client.post("/api/analysis", json={"profile_id": profile_id, "program_id": program_id})

    result = r.json()["result"]
    # Applicant's GRE is 314 (fake_profile_extraction default) -- below the 320 minimum, despite
    # 3 favorable community reports and the LLM incorrectly trying to say "Likely".
    assert result["overall_classification"] in ("Reach", "Very High Reach")
    assert result["requirement_check"]["any_hard_failure"] is True


def test_too_few_community_reports_do_not_count_as_a_signal(client):
    """A single anecdote isn't a signal -- must still fall back to Insufficient Evidence."""
    with patch("app.services.profile_extraction.generate_json", return_value=fake_profile_extraction()), \
         patch("app.services.analysis.generate_json", side_effect=_fake_hedged_target), \
         patch("app.services.program_resolution.resolve_program", side_effect=_resolve_passthrough), \
         patch("app.services.requirement_extraction.extract_requirements", return_value=dict(NO_SELECTIVITY_REQS)), \
         patch("app.services.community_outcomes.search_community_outcome_pages",
               return_value=[{"url": "https://thegradcafe.com/x", "title": "results"}]), \
         patch("app.services.web_search.fetch_page_text", return_value="One applicant reported acceptance."), \
         patch("app.services.community_outcomes.extract_outcome_evidence", return_value=[FAKE_OUTCOMES[0]]), \
         patch("app.services.rag.embed_texts", side_effect=fake_embed_texts), \
         patch("app.services.rag.embed_text", side_effect=lambda t: fake_embed_texts([t])[0]):

        profile_id, program_id = _upload_and_retrieve(client, "Another University", "MS Data Science",
                                                        "Applicants need a bachelor's degree. Minimum GPA 3.0.")
        r = client.post("/api/analysis", json={"profile_id": profile_id, "program_id": program_id})

    result = r.json()["result"]
    assert result["overall_classification"] == "Insufficient Evidence"
