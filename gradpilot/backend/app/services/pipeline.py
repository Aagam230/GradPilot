"""Async pipeline: retrieve program info + run analysis, tracked via the Job row.

Runs as a FastAPI BackgroundTask in its own DB session (the request-scoped
session is closed by the time this runs).
"""
from ..db import SessionLocal
from ..models import Job, Program, StudentProfile, Analysis
from . import web_search, rag
from .analysis import run_analysis


def run_pipeline(job_id):
    db = SessionLocal()
    try:
        job = db.get(Job, job_id)
        if not job:
            return

        try:
            job.status = "retrieving"
            db.commit()

            params = job.request_params
            profile = db.get(StudentProfile, job.profile_id)
            if not profile:
                raise ValueError("Student profile not found")

            program = Program(
                university_name=params["university_name"],
                program_name=params["program_name"],
                seed_url=params.get("seed_url"),
            )
            db.add(program)
            db.commit()
            db.refresh(program)
            job.program_id = program.id
            db.commit()

            pages = []
            manual_text = params.get("manual_text")
            if manual_text and manual_text.strip():
                pages.append({
                    "url": params.get("seed_url") or "user-provided",
                    "title": f"{program.university_name} - {program.program_name} (manually provided)",
                    "text": manual_text.strip(),
                })

            urls_to_fetch = []
            if params.get("seed_url"):
                urls_to_fetch.append({"url": params["seed_url"], "title": ""})
            urls_to_fetch += web_search.search_program_pages(program.university_name, program.program_name)

            seen = set()
            for cand in urls_to_fetch:
                url = cand["url"]
                if url in seen:
                    continue
                seen.add(url)
                text = web_search.fetch_page_text(url)
                if text:
                    pages.append({"url": url, "title": cand.get("title", ""), "text": text})
                if len(pages) >= 8:
                    break

            if pages:
                rag.ingest_pages(db, program.id, pages)

            job.status = "analyzing"
            db.commit()

            query = (
                f"{profile.structured_profile.get('summary', '')} "
                f"Program: {program.university_name} {program.program_name}. "
                "Admissions requirements, curriculum, research areas, faculty, prerequisites."
            )
            chunks = rag.retrieve_relevant_chunks(db, program.id, query, top_k=8)
            result = run_analysis(profile.structured_profile, chunks)

            record = Analysis(profile_id=profile.id, program_id=program.id, result=result)
            db.add(record)
            db.commit()
            db.refresh(record)

            job.analysis_id = record.id
            job.status = "done"
            db.commit()

        except Exception as e:
            db.rollback()
            job = db.get(Job, job_id)
            if job:
                job.status = "error"
                job.error = str(e)
                db.commit()
    finally:
        db.close()
