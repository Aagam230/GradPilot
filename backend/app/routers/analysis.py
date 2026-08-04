from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import StudentProfile, Program, Analysis
from ..services import rag
from ..services.analysis import run_analysis

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


class AnalysisRequest(BaseModel):
    profile_id: str
    program_id: str


@router.post("")
def create_analysis(req: AnalysisRequest, db: Session = Depends(get_db)):
    profile = db.get(StudentProfile, req.profile_id)
    if not profile:
        raise HTTPException(404, "Student profile not found")
    program = db.get(Program, req.program_id)
    if not program:
        raise HTTPException(404, "Program not found")

    query = (
        f"{profile.structured_profile.get('summary', '')} "
        f"Program: {program.university_name} {program.program_name}. "
        "Admissions requirements, curriculum, research areas, faculty, prerequisites."
    )
    chunks = rag.retrieve_relevant_chunks(db, program.id, query, top_k=8)

    try:
        result = run_analysis(profile.structured_profile, chunks)
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
