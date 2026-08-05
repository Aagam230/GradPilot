from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import StudentProfile, Program, Analysis
from ..services import rag
from ..services.analysis import run_analysis
from ..services.requirements import compare_hard_requirements, classify_admission

router=APIRouter(prefix="/api/analysis",tags=["analysis"])
class AnalysisRequest(BaseModel):
    profile_id:str
    program_id:str

@router.post("")
def create_analysis(req:AnalysisRequest,db:Session=Depends(get_db)):
    profile=db.get(StudentProfile,req.profile_id)
    if not profile: raise HTTPException(404,"Student profile not found")
    if not profile.structured_profile: raise HTTPException(400,"Upload at least one document before running analysis.")
    program=db.get(Program,req.program_id)
    if not program: raise HTTPException(404,"Program not found")
    query=f"{profile.structured_profile.get('summary','')} Program: {program.university_name} {program.program_name}. Admissions requirements curriculum prerequisites competitiveness."
    chunks=rag.retrieve_relevant_chunks(db,program.id,query,top_k=8)
    requirements=program.structured_requirements or {}
    checks=compare_hard_requirements(profile.structured_profile,requirements)
    assessment=classify_admission(profile.structured_profile,requirements,checks)
    try: result=run_analysis(profile.structured_profile,chunks,requirements,checks,assessment)
    except Exception as e: raise HTTPException(502,f"Analysis generation failed: {e}")
    result["program_resolution"]={"canonical_university_name":program.university_name,"canonical_program_name":program.program_name,"official_domain":program.official_domain,"program_url":program.seed_url}
    record=Analysis(profile_id=profile.id,program_id=program.id,result=result); db.add(record); db.commit(); db.refresh(record)
    return {"analysis_id":str(record.id),"result":result}

@router.get("/{analysis_id}")
def get_analysis(analysis_id:str,db:Session=Depends(get_db)):
    record=db.get(Analysis,analysis_id)
    if not record: raise HTTPException(404,"Analysis not found")
    return {"analysis_id":str(record.id),"result":record.result}
