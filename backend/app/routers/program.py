from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Program, ProgramChunk
from ..services import program_pipeline

router = APIRouter(prefix="/api/program", tags=["program"])


class ProgramCreateRequest(BaseModel):
    university_name: str
    program_name: str
    seed_url: str | None = None
    # Optional manual fallback: paste official program page text directly
    # (useful when live web search is unavailable in this environment).
    manual_text: str | None = None


@router.post("/retrieve")
def retrieve_program(req: ProgramCreateRequest, db: Session = Depends(get_db)):
    program, pages = program_pipeline.get_or_build_program(
        db,
        university_name=req.university_name,
        program_name=req.program_name,
        seed_url=req.seed_url,
        manual_text=req.manual_text,
    )

    n_chunks = db.query(ProgramChunk).filter(ProgramChunk.program_id == program.id).count()
    response = {
        "program_id": str(program.id),
        "canonical_university": program.canonical_university,
        "canonical_program": program.canonical_program,
        "chunks_ingested": n_chunks,
        "sources": [{"url": p["url"], "title": p["title"]} for p in pages],
        "structured_requirements": program.structured_requirements,
    }
    if n_chunks == 0:
        response["warning"] = (
            "Insufficient evidence: no official program information could be retrieved. "
            "Configure TAVILY_API_KEY, provide a seed_url, or paste manual_text."
        )
    return response


@router.get("/{program_id}")
def get_program(program_id: str, db: Session = Depends(get_db)):
    program = db.get(Program, program_id)
    if not program:
        raise HTTPException(404, "Program not found")
    n_chunks = db.query(ProgramChunk).filter(ProgramChunk.program_id == program_id).count()
    return {
        "program_id": str(program.id),
        "university_name": program.university_name,
        "program_name": program.program_name,
        "canonical_university": program.canonical_university,
        "canonical_program": program.canonical_program,
        "chunks": n_chunks,
        "structured_requirements": program.structured_requirements,
    }
