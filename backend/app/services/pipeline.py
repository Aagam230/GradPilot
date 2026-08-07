"""Async pipeline: retrieve program info + run analysis, tracked via the Job row.

Runs as a FastAPI BackgroundTask in its own DB session (the request-scoped
session is closed by the time this runs).
"""
from ..db import SessionLocal
from ..models import Job, StudentProfile, Analysis
from . import rag, program_pipeline, requirement_check as requirement_check_svc
from .analysis import run_analysis
from .applicant_strength import build_applicant_strength


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

            program, _pages = program_pipeline.get_or_build_program(
                db,
                university_name=params["university_name"],
                program_name=params["program_name"],
                seed_url=params.get("seed_url"),
                manual_text=params.get("manual_text"),
            )
            job.program_id = program.id
            db.commit()

            job.status = "analyzing"
            db.commit()

            query = (
                f"{profile.structured_profile.get('summary', '')} "
                f"Program: {program.canonical_university or program.university_name} "
                f"{program.canonical_program or program.program_name}. "
                "Admissions requirements, curriculum, research areas, faculty, prerequisites."
            )
            chunks = rag.retrieve_relevant_chunks(db, program.id, query, top_k=8)
            requirements = program.structured_requirements or {}
            req_check = requirement_check_svc.check_requirements(profile.structured_profile, requirements)
            result = run_analysis(
                profile.structured_profile, chunks, requirements, req_check,
                program.community_outcome_evidence,
                build_applicant_strength(profile.structured_profile),
            )

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
