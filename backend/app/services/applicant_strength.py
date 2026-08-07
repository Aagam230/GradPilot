"""Deterministic evidence summary of the applicant's uploaded application packet.

This does not predict admission. It makes the LLM consume the full profile consistently instead of
free-form judging a resume. Ratings are deliberately coarse and evidence/completeness are explicit.
"""
import re


def _num(text):
    m = re.search(r"(\d+(?:\.\d+)?)", str(text or ""))
    return float(m.group(1)) if m else None


def build_applicant_strength(profile: dict) -> dict:
    education = profile.get("education") or []
    research = profile.get("research_experience") or []
    projects = profile.get("projects") or []
    work = profile.get("work_experience") or []
    publications = profile.get("publications") or []
    skills = profile.get("skills") or []
    coursework = profile.get("coursework_highlights") or []
    awards = profile.get("awards") or []
    tests = profile.get("test_scores") or []

    gpa = next((_num(e.get("gpa")) for e in education if _num(e.get("gpa")) is not None), None)
    gre = next((_num(t.get("score")) for t in tests if "gre" in (t.get("test") or "").lower()), None)
    english = next((_num(t.get("score")) for t in tests if any(k in (t.get("test") or "").lower() for k in ("toefl", "ielts"))), None)

    present = {
        "education": bool(education), "gpa": gpa is not None, "research": bool(research),
        "projects": bool(projects), "work_experience": bool(work), "publications": bool(publications),
        "skills": bool(skills), "coursework": bool(coursework), "test_scores": bool(tests),
    }
    completeness = round(sum(present.values()) / len(present), 2)

    research_rating = "Strong" if len(publications) >= 2 or (publications and research) else "Moderate" if research or publications else "Limited"
    project_rating = "Strong" if len(projects) >= 2 else "Moderate" if projects else "Limited"
    experience_rating = "Strong" if len(work) >= 2 else "Moderate" if work else "Limited"
    academic_rating = "Evidence Available" if education and gpa is not None else "Partial Evidence" if education else "Unknown"

    return {
        "academics": {"rating": academic_rating, "gpa_extracted": gpa, "coursework_count": len(coursework)},
        "research": {"rating": research_rating, "research_entries": len(research), "publication_count": len(publications)},
        "projects": {"rating": project_rating, "project_count": len(projects)},
        "experience": {"rating": experience_rating, "experience_entries": len(work)},
        "technical_evidence": {"skill_count": len(skills), "award_count": len(awards)},
        "tests": {"gre_extracted": gre, "english_test_extracted": english, "test_entries": len(tests)},
        "profile_completeness": completeness,
        "evidence_presence": present,
        "note": "This is a structured evidence summary, not an admission prediction or university-relative score.",
    }
