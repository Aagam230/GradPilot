"""Shared program resolution + retrieval + structured-requirement extraction, used by both the
sync /api/program/retrieve endpoint and the async job pipeline so they stay consistent instead of
duplicating (and potentially diverging) logic.
"""
import re
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..models import Program
from . import web_search, rag, program_resolution, requirement_extraction, community_outcomes
from ..config import settings


def _tokens(s: str) -> list[str]:
    return [t.lower() for t in re.findall(r"[A-Za-z]+", s or "") if len(t) > 3]


def get_or_build_program(
    db: Session,
    university_name: str,
    program_name: str,
    seed_url: str | None = None,
    manual_text: str | None = None,
) -> tuple[Program, list[dict]]:
    """Returns (program, newly_fetched_pages). Reuses an existing canonical program (with its
    cached evidence + structured requirements) when the input resolves to one already retrieved —
    this is what makes equivalent aliases ("MS in Computing" vs "MSc in Computing") produce the
    same evidence and classification instead of independent, inconsistent results.

    IMPORTANT: user-supplied seed_url/manual_text is never merged into the SHARED canonical
    program. It's untrusted, unverified input from one requester — mixing it into the pool other
    requesters' equivalent-alias lookups land on would let one person's pasted text (wrong,
    outdated, or deliberately false) silently poison what everyone else sees for that program.
    Such requests always get their own isolated, non-shared row instead.
    """
    is_user_provided = bool((manual_text and manual_text.strip()) or seed_url)

    resolved = program_resolution.resolve_program(university_name, program_name)
    canonical_university = resolved["canonical_university"]
    canonical_program = resolved["canonical_program"]
    official_domain = resolved["official_domain"]

    existing = None
    if canonical_university and canonical_program and not is_user_provided:
        existing = (
            db.query(Program)
            .filter(
                func.lower(Program.canonical_university) == canonical_university.lower(),
                func.lower(Program.canonical_program) == canonical_program.lower(),
                Program.user_provided_only.is_(False),
            )
            .first()
        )

    # Cache hit: reuse the existing SHARED program's evidence/requirements untouched — no
    # re-scraping. Never applies to user-provided requests (see docstring).
    community_ready = (not settings.enable_community_outcome_evidence) or (
        existing is not None and existing.community_outcome_evidence is not None
    )
    if existing and existing.structured_requirements and community_ready and not is_user_provided:
        return existing, []

    program = existing if not is_user_provided else None
    if program is None:
        program = Program(
            university_name=university_name,
            program_name=program_name,
            seed_url=seed_url,
            user_provided_only=is_user_provided,
        )
        db.add(program)
    program.canonical_university = canonical_university
    program.canonical_program = canonical_program
    program.official_domain = program.official_domain or official_domain
    if seed_url:
        program.program_url = seed_url
    db.commit()
    db.refresh(program)

    pages = []
    if manual_text and manual_text.strip():
        pages.append({
            "url": seed_url or "user-provided",
            "title": f"{canonical_university} - {canonical_program} (manually provided)",
            "text": manual_text.strip(),
        })

    urls_to_fetch = []
    if seed_url:
        urls_to_fetch.append({"url": seed_url, "title": ""})
    if canonical_university:
        urls_to_fetch += web_search.search_program_pages(
            canonical_university, canonical_program, official_domain=official_domain
        )

    university_tokens = _tokens(canonical_university)
    seen = set()
    for cand in urls_to_fetch:
        url = cand["url"]
        if url in seen:
            continue
        seen.add(url)
        text = web_search.fetch_page_text(url)
        if not text:
            continue
        # Reject pages that don't even mention the resolved university anywhere — rejects clearly
        # unrelated content that slipped past search (wrong school, wrong campus, off-topic page).
        if university_tokens and not any(t in text.lower() for t in university_tokens):
            continue
        pages.append({"url": url, "title": cand.get("title", ""), "text": text})
        if len(pages) >= 8:
            break

    if pages:
        rag.ingest_pages(db, program.id, pages)

    # (Re)compute structured requirements whenever we fetched anything new, or never had them.
    if pages or not program.structured_requirements:
        req_chunks = rag.retrieve_relevant_chunks(
            db, program.id,
            f"{canonical_program} admissions requirements prerequisites GPA GRE TOEFL IELTS "
            f"degree background eligibility pathways related discipline computing specialisation "
            f"work experience exceptions FAQ selectivity acceptance rate",
            top_k=12,
        )
        program.structured_requirements = requirement_extraction.extract_requirements(req_chunks)
        db.commit()
        db.refresh(program)

    # Community-reported outcomes: a separate, capped-trust tier (see community_outcomes.py).
    # Only (re)fetched under the same conditions as structured_requirements, and independently
    # toggleable via ENABLE_COMMUNITY_OUTCOME_EVIDENCE. Community search is always keyed off the
    # resolved canonical name, never off user-provided text, so this isn't a poisoning vector.
    if settings.enable_community_outcome_evidence and (pages or not program.community_outcome_evidence):
        if canonical_university:
            candidates = community_outcomes.search_community_outcome_pages(canonical_university, canonical_program)
            outcome_pages = []
            seen_outcome_urls = set()
            for cand in candidates:
                url = cand["url"]
                if url in seen_outcome_urls:
                    continue
                seen_outcome_urls.add(url)
                text = web_search.fetch_page_text(url)
                if text:
                    outcome_pages.append({"url": url, "title": cand.get("title", ""), "text": text})
                if len(outcome_pages) >= 4:
                    break
            program.community_outcome_evidence = community_outcomes.extract_outcome_evidence(outcome_pages)
            db.commit()
            db.refresh(program)

    return program, pages
