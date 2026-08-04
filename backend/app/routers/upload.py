from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import StudentProfile
from ..services.pdf_extract import extract_pdf_text
from ..services.profile_extraction import extract_profile

router = APIRouter(prefix="/api/profile", tags=["profile"])

MAX_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/upload")
async def upload_cv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Only PDF files are supported.")
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(400, "File too large (max 10MB).")

    try:
        text = extract_pdf_text(content)
    except ValueError as e:
        raise HTTPException(422, str(e))

    try:
        structured = extract_profile(text)
    except Exception as e:
        raise HTTPException(502, f"Profile extraction failed: {e}")

    profile = StudentProfile(raw_text=text, structured_profile=structured, source_filename=file.filename)
    db.add(profile)
    db.commit()
    db.refresh(profile)

    return {"profile_id": str(profile.id), "profile": structured}


@router.get("/{profile_id}")
def get_profile(profile_id: str, db: Session = Depends(get_db)):
    profile = db.get(StudentProfile, profile_id)
    if not profile:
        raise HTTPException(404, "Profile not found")
    return {"profile_id": str(profile.id), "profile": profile.structured_profile}
