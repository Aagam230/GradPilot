from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Program, ProgramChunk
from ..services import web_search, rag

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
    program = Program(university_name=req.university_name, program_name=req.program_name, seed_url=req.seed_url)
    db.add(program)
    db.commit()
    db.refresh(program)

    pages = []

    if req.manual_text and req.manual_text.strip():
        pages.append({
            "url": req.seed_url or "user-provided",
            "title": f"{req.university_name} - {req.program_name} (manually provided)",
            "text": req.manual_text.strip(),
        })

    urls_to_fetch = []
    if req.seed_url:
        urls_to_fetch.append({"url": req.seed_url, "title": ""})
    urls_to_fetch += web_search.search_program_pages(req.university_name, req.program_name)

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

    if not pages:
        return {
            "program_id": str(program.id),
            "chunks_ingested": 0,
            "sources": [],
            "warning": "Insufficient evidence: no official program information could be retrieved. "
                       "Configure TAVILY_API_KEY, provide a seed_url, or paste manual_text.",
        }

    count = rag.ingest_pages(db, program.id, pages)
    return {
        "program_id": str(program.id),
        "chunks_ingested": count,
        "sources": [{"url": p["url"], "title": p["title"]} for p in pages],
    }


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
        "chunks": n_chunks,
    }
