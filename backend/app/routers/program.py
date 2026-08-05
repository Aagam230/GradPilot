from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Program, ProgramChunk
from ..services import web_search, rag
from ..services.program_resolution import resolve_program, domain_from_url
from ..services.requirements import extract_requirements

router = APIRouter(prefix="/api/program", tags=["program"])

class ProgramCreateRequest(BaseModel):
    university_name: str
    program_name: str
    seed_url: str | None = None
    manual_text: str | None = None

@router.post("/retrieve")
def retrieve_program(req: ProgramCreateRequest, db: Session = Depends(get_db)):
    resolved = resolve_program(req.university_name, req.program_name, req.seed_url)
    program = Program(university_name=resolved["canonical_university_name"], program_name=resolved["canonical_program_name"], seed_url=req.seed_url, official_domain=resolved["official_domain"])
    db.add(program); db.commit(); db.refresh(program)
    pages = []
    if req.manual_text and req.manual_text.strip():
        pages.append({"url": req.seed_url or "user-provided", "title": f"{program.university_name} - {program.program_name} (manually provided)", "text": req.manual_text.strip(), "official": bool(req.seed_url)})
    urls = []
    if req.seed_url:
        sd = domain_from_url(req.seed_url)
        if not program.official_domain or (sd and (sd == program.official_domain or sd.endswith('.'+program.official_domain))):
            urls.append({"url": req.seed_url, "title": "", "official": True})
    urls += web_search.search_program_pages(program.university_name, program.program_name, official_domain=program.official_domain)
    seen=set()
    for cand in urls:
        if cand["url"] in seen: continue
        seen.add(cand["url"]); text=web_search.fetch_page_text(cand["url"])
        if text: pages.append({**cand,"text":text})
        if len(pages)>=8: break
    if not pages:
        return {"program_id":str(program.id),"chunks_ingested":0,"sources":[],"canonical_university_name":program.university_name,"canonical_program_name":program.program_name,"official_domain":program.official_domain,"warning":"Insufficient evidence: no official program information could be retrieved."}
    count=rag.ingest_pages(db,program.id,pages)
    program.structured_requirements=extract_requirements([p for p in pages if p.get("official")]); db.commit()
    return {"program_id":str(program.id),"chunks_ingested":count,"sources":[{"url":p["url"],"title":p["title"]} for p in pages],"canonical_university_name":program.university_name,"canonical_program_name":program.program_name,"official_domain":program.official_domain,"structured_requirements":program.structured_requirements}

@router.get("/{program_id}")
def get_program(program_id:str, db:Session=Depends(get_db)):
    program=db.get(Program,program_id)
    if not program: raise HTTPException(404,"Program not found")
    n=db.query(ProgramChunk).filter(ProgramChunk.program_id==program_id).count()
    return {"program_id":str(program.id),"university_name":program.university_name,"program_name":program.program_name,"official_domain":program.official_domain,"structured_requirements":program.structured_requirements,"chunks":n}
