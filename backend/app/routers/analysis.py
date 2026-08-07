from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import StudentProfile, Program, Analysis
from ..services import rag, requirement_check as requirement_check_svc
from ..services.analysis import run_analysis
from ..services.applicant_strength import build_applicant_strength

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


class AnalysisRequest(BaseModel):
    profile_id: str
    program_id: str


@router.post("")
def create_analysis(req: AnalysisRequest, db: Session = Depends(get_db)):
    profile = db.get(StudentProfile, req.profile_id)
    if not profile:
        raise HTTPException(404, "Student profile not found")
    if not profile.structured_profile:
        raise HTTPException(400, "Upload at least one document before running analysis.")
    program = db.get(Program, req.program_id)
    if not program:
        raise HTTPException(404, "Program not found")

    query = (
        f"{profile.structured_profile.get('summary', '')} "
        f"Program: {program.canonical_university or program.university_name} "
        f"{program.canonical_program or program.program_name}. "
        "Admissions requirements, curriculum, research areas, faculty, prerequisites."
    )
    chunks = rag.retrieve_relevant_chunks(db, program.id, query, top_k=8)
    requirements = program.structured_requirements or {}
    req_check = requirement_check_svc.check_requirements(profile.structured_profile, requirements)

    try:
        result = run_analysis(
            profile.structured_profile, chunks, requirements, req_check,
            program.community_outcome_evidence,
            build_applicant_strength(profile.structured_profile),
        )
    except Exception as e:
        raise HTTPException(502, f"Analysis generation failed: {e}")

    record = Analysis(profile_id=profile.id, program_id=program.id, result=result)
    db.add(record)
    db.commit()
    db.refresh(record)

    return {"analysis_id": str(record.id), "result": result}


@router.get("/{analysis_id}")
def get_analysis(analysis_id: str, db: Session = Depends(get_db)):
    record = db.get(Analysis, analysis_id)
    if not record:
        raise HTTPException(404, "Analysis not found")
    return {"analysis_id": str(record.id), "result": record.result}
