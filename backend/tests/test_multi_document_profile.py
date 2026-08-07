from unittest.mock import patch
from tests.conftest import fake_profile_extraction, fake_embed_texts


def test_upload_creates_profile(client, sample_cv_bytes):
    with patch("app.services.profile_extraction.generate_json", return_value=fake_profile_extraction()):
        r = client.post(
            "/api/profile/upload",
            files={"file": ("cv.pdf", sample_cv_bytes, "application/pdf")},
            data={"doc_type": "cv"},
        )
    assert r.status_code == 200
    data = r.json()
    assert data["profile"]["name"] == "Jane Doe"
    assert len(data["documents"]) == 1
    assert data["documents"][0]["doc_type"] == "cv"


def test_second_document_merges_into_same_profile(client, sample_cv_bytes):
    def fake_merge(system, user, max_tokens=2000, **kw):
        has_transcript = 'type="Academic Transcript"' in user
        return fake_profile_extraction(
            coursework_highlights=["CS 6.867 Machine Learning: A"] if has_transcript else []
        )

    with patch("app.services.profile_extraction.generate_json", side_effect=fake_merge):
        r = client.post(
            "/api/profile/upload",
            files={"file": ("cv.pdf", sample_cv_bytes, "application/pdf")},
            data={"doc_type": "cv"},
        )
        profile_id = r.json()["profile_id"]
        assert r.json()["profile"]["coursework_highlights"] == []

        r = client.post(
            "/api/profile/upload",
            files={"file": ("transcript.pdf", sample_cv_bytes, "application/pdf")},
            data={"doc_type": "transcript", "profile_id": profile_id},
        )
    assert r.status_code == 200
    assert r.json()["profile"]["coursework_highlights"] == ["CS 6.867 Machine Learning: A"]
    assert len(r.json()["documents"]) == 2


def test_replace_on_upload_for_single_instance_types(client, sample_cv_bytes):
    with patch("app.services.profile_extraction.generate_json", return_value=fake_profile_extraction()):
        r = client.post(
            "/api/profile/upload",
            files={"file": ("cv_v1.pdf", sample_cv_bytes, "application/pdf")},
            data={"doc_type": "cv"},
        )
        profile_id = r.json()["profile_id"]

        r = client.post(
            "/api/profile/upload",
            files={"file": ("cv_v2.pdf", sample_cv_bytes, "application/pdf")},
            data={"doc_type": "cv", "profile_id": profile_id},
        )
    docs = r.json()["documents"]
    cv_docs = [d for d in docs if d["doc_type"] == "cv"]
    assert len(cv_docs) == 1
    assert cv_docs[0]["filename"] == "cv_v2.pdf"


def test_manual_correction_survives_document_rebuild(client, sample_cv_bytes):
    """A student-corrected field (e.g. a misread GPA) must not silently revert when a new
    document is added and the profile is re-extracted from scratch."""

    def fake_wrong_gpa(system, user, max_tokens=2000, **kw):
        return fake_profile_extraction(
            education=[{"degree": "BSc", "field": "CS", "institution": "MIT", "gpa": "3.5", "years": "2020-2024"}]
        )

    with patch("app.services.profile_extraction.generate_json", side_effect=fake_wrong_gpa):
        r = client.post(
            "/api/profile/upload",
            files={"file": ("cv.pdf", sample_cv_bytes, "application/pdf")},
            data={"doc_type": "cv"},
        )
        profile_id = r.json()["profile_id"]
        assert r.json()["profile"]["education"][0]["gpa"] == "3.5"

        corrected = [{"degree": "BSc", "field": "CS", "institution": "MIT", "gpa": "3.85", "years": "2020-2024"}]
        r = client.patch(f"/api/profile/{profile_id}", json={"education": corrected})
        assert r.json()["profile"]["education"][0]["gpa"] == "3.85"

        r = client.post(
            "/api/profile/upload",
            files={"file": ("transcript.pdf", sample_cv_bytes, "application/pdf")},
            data={"doc_type": "transcript", "profile_id": profile_id},
        )
    assert r.json()["profile"]["education"][0]["gpa"] == "3.85"


def test_patch_rejects_unknown_fields(client, sample_cv_bytes):
    with patch("app.services.profile_extraction.generate_json", return_value=fake_profile_extraction()):
        r = client.post(
            "/api/profile/upload",
            files={"file": ("cv.pdf", sample_cv_bytes, "application/pdf")},
            data={"doc_type": "cv"},
        )
    profile_id = r.json()["profile_id"]
    r = client.patch(f"/api/profile/{profile_id}", json={"id": "hacked"})
    assert r.status_code == 400


def test_analysis_blocked_with_no_documents(client, sample_cv_bytes):
    with patch("app.services.profile_extraction.generate_json", return_value=fake_profile_extraction()):
        r = client.post(
            "/api/profile/upload",
            files={"file": ("cv.pdf", sample_cv_bytes, "application/pdf")},
            data={"doc_type": "cv"},
        )
    profile_id = r.json()["profile_id"]
    doc_id = r.json()["documents"][0]["id"]
    client.delete(f"/api/profile/{profile_id}/documents/{doc_id}")

    r = client.post("/api/jobs", json={"profile_id": profile_id, "university_name": "X", "program_name": "Y"})
    assert r.status_code == 400
