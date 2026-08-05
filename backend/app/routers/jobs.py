from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Job, StudentProfile
from ..services.pipeline import run_pipeline

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


class JobCreateRequest(BaseModel):
    profile_id: str
    university_name: str
    program_name: str
    seed_url: str | None = None
    manual_text: str | None = None


@router.post("")
def create_job(req: JobCreateRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    profile = db.get(StudentProfile, req.profile_id)
    if not profile:
        raise HTTPException(404, "Student profile not found")
    if not profile.structured_profile:
        raise HTTPException(400, "Upload at least one document before running analysis.")

    job = Job(
        profile_id=profile.id,
        status="pending",
        request_params={
            "university_name": req.university_name,
            "program_name": req.program_name,
            "seed_url": req.seed_url,
            "manual_text": req.manual_text,
        },
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(run_pipeline, job.id)
    return {"job_id": str(job.id), "status": job.status}


@router.get("/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return {
        "job_id": str(job.id),
        "status": job.status,
        "program_id": str(job.program_id) if job.program_id else None,
        "analysis_id": str(job.analysis_id) if job.analysis_id else None,
        "error": job.error,
    }
