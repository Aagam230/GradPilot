from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import StudentProfile, Document, DOCUMENT_TYPES
from ..services.pdf_extract import extract_pdf_text
from ..services.profile_extraction import extract_profile_from_documents

router = APIRouter(prefix="/api/profile", tags=["profile"])

MAX_SIZE = 10 * 1024 * 1024  # 10MB


def _rebuild_profile(db: Session, profile: StudentProfile) -> dict:
    docs = (
        db.query(Document)
        .filter(Document.profile_id == profile.id)
        .order_by(Document.created_at)
        .all()
    )
    if not docs:
        structured = {}
    else:
        try:
            structured = extract_profile_from_documents(
                [{"doc_type": d.doc_type, "text": d.raw_text} for d in docs]
            )
        except Exception as e:
            raise HTTPException(502, f"Profile extraction failed: {e}")
    profile.structured_profile = structured
    db.commit()
    db.refresh(profile)
    return structured


def _doc_summary(d: Document) -> dict:
    return {
        "id": str(d.id),
        "doc_type": d.doc_type,
        "filename": d.filename,
        "created_at": d.created_at.isoformat() if d.created_at else None,
    }


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form("cv"),
    profile_id: str | None = Form(None),
    db: Session = Depends(get_db),
):
    if doc_type not in DOCUMENT_TYPES:
        raise HTTPException(400, f"doc_type must be one of {DOCUMENT_TYPES}")
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Only PDF files are supported.")
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(400, "File too large (max 10MB).")

    try:
        text = extract_pdf_text(content)
    except ValueError as e:
        raise HTTPException(422, str(e))

    if profile_id:
        profile = db.get(StudentProfile, profile_id)
        if not profile:
            raise HTTPException(404, "Profile not found")
    else:
        profile = StudentProfile(structured_profile={})
        db.add(profile)
        db.commit()
        db.refresh(profile)

    doc = Document(profile_id=profile.id, doc_type=doc_type, filename=file.filename, raw_text=text)
    db.add(doc)
    db.commit()

    structured = _rebuild_profile(db, profile)

    docs = db.query(Document).filter(Document.profile_id == profile.id).order_by(Document.created_at).all()
    return {
        "profile_id": str(profile.id),
        "profile": structured,
        "documents": [_doc_summary(d) for d in docs],
    }


@router.get("/{profile_id}")
def get_profile(profile_id: str, db: Session = Depends(get_db)):
    profile = db.get(StudentProfile, profile_id)
    if not profile:
        raise HTTPException(404, "Profile not found")
    docs = db.query(Document).filter(Document.profile_id == profile_id).order_by(Document.created_at).all()
    return {
        "profile_id": str(profile.id),
        "profile": profile.structured_profile,
        "documents": [_doc_summary(d) for d in docs],
    }


@router.delete("/{profile_id}/documents/{document_id}")
def delete_document(profile_id: str, document_id: str, db: Session = Depends(get_db)):
    profile = db.get(StudentProfile, profile_id)
    if not profile:
        raise HTTPException(404, "Profile not found")
    doc = db.get(Document, document_id)
    if not doc or str(doc.profile_id) != profile_id:
        raise HTTPException(404, "Document not found")
    db.delete(doc)
    db.commit()

    structured = _rebuild_profile(db, profile)
    docs = db.query(Document).filter(Document.profile_id == profile_id).order_by(Document.created_at).all()
    return {
        "profile_id": str(profile.id),
        "profile": structured,
        "documents": [_doc_summary(d) for d in docs],
    }
