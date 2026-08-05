"""Async retrieve -> structured requirements -> deterministic assessment -> LLM explanation."""
from ..db import SessionLocal
from ..models import Job, Program, StudentProfile, Analysis
from . import web_search, rag
from .analysis import run_analysis
from .program_resolution import resolve_program, domain_from_url
from .requirements import extract_requirements, compare_hard_requirements, classify_admission


def run_pipeline(job_id):
    db = SessionLocal()
    try:
        job = db.get(Job, job_id)
        if not job: return
        try:
            job.status = "retrieving"; db.commit()
            params = job.request_params
            profile = db.get(StudentProfile, job.profile_id)
            if not profile: raise ValueError("Student profile not found")

            resolved = resolve_program(params["university_name"], params["program_name"], params.get("seed_url"))
            program = Program(
                university_name=resolved["canonical_university_name"],
                program_name=resolved["canonical_program_name"], seed_url=params.get("seed_url"),
                official_domain=resolved["official_domain"],
            )
            db.add(program); db.commit(); db.refresh(program)
            job.program_id = program.id; db.commit()

            pages = []
            manual_text = params.get("manual_text")
            if manual_text and manual_text.strip():
                pages.append({"url": params.get("seed_url") or "user-provided", "title": f"{program.university_name} - {program.program_name} (manually provided)", "text": manual_text.strip(), "official": bool(params.get("seed_url"))})

            urls = []
            if params.get("seed_url"):
                seed_domain = domain_from_url(params["seed_url"])
                if not program.official_domain or (seed_domain and (seed_domain == program.official_domain or seed_domain.endswith('.'+program.official_domain))):
                    urls.append({"url": params["seed_url"], "title": "", "official": True})
            urls += web_search.search_program_pages(program.university_name, program.program_name, official_domain=program.official_domain)
            seen = set()
            for cand in urls:
                if cand["url"] in seen: continue
                seen.add(cand["url"])
                text = web_search.fetch_page_text(cand["url"])
                if text: pages.append({**cand, "text": text})
                if len(pages) >= 8: break

            if pages: rag.ingest_pages(db, program.id, pages)
            req = extract_requirements([p for p in pages if p.get("official")])
            program.structured_requirements = req; db.commit()

            job.status = "analyzing"; db.commit()
            query = f"{profile.structured_profile.get('summary','')} Program: {program.university_name} {program.program_name}. Admissions requirements curriculum prerequisites competitiveness."
            chunks = rag.retrieve_relevant_chunks(db, program.id, query, top_k=8) if pages else []
            checks = compare_hard_requirements(profile.structured_profile, req)
            assessment = classify_admission(profile.structured_profile, req, checks)
            result = run_analysis(profile.structured_profile, chunks, req, checks, assessment)
            result["program_resolution"] = {"canonical_university_name": program.university_name, "canonical_program_name": program.program_name, "official_domain": program.official_domain, "program_url": program.seed_url}

            record = Analysis(profile_id=profile.id, program_id=program.id, result=result)
            db.add(record); db.commit(); db.refresh(record)
            job.analysis_id = record.id; job.status = "done"; db.commit()
        except Exception as e:
            db.rollback(); job = db.get(Job, job_id)
            if job: job.status = "error"; job.error = str(e); db.commit()
    finally:
        db.close()
