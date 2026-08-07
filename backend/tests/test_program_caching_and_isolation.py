from unittest.mock import patch
from tests.conftest import fake_profile_extraction, fake_embed_texts

BASE_REQS = {
    "minimum_gpa": 3.0, "gre_required": False, "gre_minimum": None, "toefl_minimum": None,
    "ielts_minimum": None, "required_background": [], "required_prerequisites": [],
    "work_experience_required": None, "work_experience_preferred": None,
    "research_expectations": None, "selectivity_evidence": [], "sources": {},
}


def _fake_nus_resolve(university_name, program_name):
    u = university_name.lower()
    if "nus" in u or "national university of singapore" in u:
        # ALL wordings of the NUS CS master's resolve to the identical canonical string
        return {"canonical_university": "National University of Singapore",
                "canonical_program": "Master of Computing in Computer Science", "official_domain": "nus.edu.sg"}
    return {"canonical_university": university_name, "canonical_program": program_name, "official_domain": None}


def test_equivalent_aliases_share_one_program_via_auto_retrieval(client):
    """Different wordings of the same program, retrieved via normal auto-search (not manual_text),
    must resolve to the SAME program row -- otherwise "MS in Computing" and "MSc in Computing"
    silently become independent, potentially inconsistent programs."""
    with patch("app.services.program_resolution.resolve_program", side_effect=_fake_nus_resolve), \
         patch("app.services.requirement_extraction.extract_requirements", return_value=dict(BASE_REQS)), \
         patch("app.services.web_search.search_program_pages",
               return_value=[{"url": "https://nus.edu.sg/admissions", "title": "Admissions"}]), \
         patch("app.services.web_search.fetch_page_text",
               return_value="National University of Singapore Master of Computing admissions info. " * 5), \
         patch("app.services.community_outcomes.search_community_outcome_pages", return_value=[]), \
         patch("app.services.rag.embed_texts", side_effect=fake_embed_texts), \
         patch("app.services.rag.embed_text", side_effect=lambda t: fake_embed_texts([t])[0]):

        r1 = client.post("/api/program/retrieve", json={"university_name": "NUS", "program_name": "Master of Computing"})
        r2 = client.post("/api/program/retrieve", json={"university_name": "National University of Singapore", "program_name": "MS in Computing"})
        r3 = client.post("/api/program/retrieve", json={"university_name": "NUS", "program_name": "Master of Computing (Computer Science Specialisation)"})

    ids = {r1.json()["program_id"], r2.json()["program_id"], r3.json()["program_id"]}
    assert len(ids) == 1, f"expected all aliases to share one program, got {ids}"


def test_user_provided_manual_text_never_pollutes_shared_program(client):
    """User A pastes fake/wrong manual_text for a program. User B later queries the SAME
    canonical program via normal auto-retrieval and must NOT see User A's data or even land on
    the same row."""
    def resolve_harvard(university_name, program_name):
        return {"canonical_university": "Harvard University",
                "canonical_program": "Master of Science in Computer Science", "official_domain": "harvard.edu"}

    def extract_reqs(chunks):
        text = " ".join(c.content for c in chunks) if chunks else ""
        if "200" in text:
            return dict(BASE_REQS, gre_required=True, gre_minimum=200)
        return dict(BASE_REQS)

    with patch("app.services.program_resolution.resolve_program", side_effect=resolve_harvard), \
         patch("app.services.requirement_extraction.extract_requirements", side_effect=extract_reqs), \
         patch("app.services.web_search.search_program_pages",
               return_value=[{"url": "https://harvard.edu/admissions", "title": "Admissions"}]), \
         patch("app.services.web_search.fetch_page_text",
               return_value="Harvard MS CS admissions requirements information page. " * 5), \
         patch("app.services.community_outcomes.search_community_outcome_pages", return_value=[]), \
         patch("app.services.rag.embed_texts", side_effect=fake_embed_texts), \
         patch("app.services.rag.embed_text", side_effect=lambda t: fake_embed_texts([t])[0]):

        r_a = client.post("/api/program/retrieve", json={
            "university_name": "Harvard", "program_name": "MS CS",
            "manual_text": "GRE required, minimum 200 (fake data pasted by one user).",
        })
        r_b = client.post("/api/program/retrieve", json={
            "university_name": "Harvard University", "program_name": "Master of Science in Computer Science",
        })

    assert r_a.json()["program_id"] != r_b.json()["program_id"]
    assert r_b.json()["structured_requirements"]["gre_minimum"] != 200


def test_two_different_manual_submissions_never_share_a_row(client):
    def resolve_harvard(university_name, program_name):
        return {"canonical_university": "Harvard University",
                "canonical_program": "Master of Science in Computer Science", "official_domain": "harvard.edu"}

    with patch("app.services.program_resolution.resolve_program", side_effect=resolve_harvard), \
         patch("app.services.requirement_extraction.extract_requirements", return_value=dict(BASE_REQS)), \
         patch("app.services.community_outcomes.search_community_outcome_pages", return_value=[]), \
         patch("app.services.rag.embed_texts", side_effect=fake_embed_texts), \
         patch("app.services.rag.embed_text", side_effect=lambda t: fake_embed_texts([t])[0]):

        r1 = client.post("/api/program/retrieve", json={
            "university_name": "Harvard", "program_name": "MS CS", "manual_text": "First user's pasted text here.",
        })
        r2 = client.post("/api/program/retrieve", json={
            "university_name": "Harvard", "program_name": "MS CS", "manual_text": "Second user's completely different text.",
        })

    assert r1.json()["program_id"] != r2.json()["program_id"]
