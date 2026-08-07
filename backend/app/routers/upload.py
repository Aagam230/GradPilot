from fastapi import APIRouter, UploadFile, File, Form, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from ..db import get_db
from ..models import StudentProfile, Document, DOCUMENT_TYPES
from ..services.pdf_extract import extract_pdf_text
from ..services.profile_extraction import extract_profile_from_documents

# These document types represent one canonical document per profile — re-uploading replaces the
# previous one rather than stacking duplicates (e.g. a second CV shouldn't merge alongside the first).
SINGLE_INSTANCE_TYPES = {"cv", "transcript", "gre", "toefl_ielts", "sop"}

# Only these top-level structured_profile fields can be manually edited/overridden by the student —
# keeps PATCH from accepting arbitrary junk keys into the profile.
EDITABLE_FIELDS = {
    "name", "education", "research_experience", "projects", "work_experience",
    "publications", "skills", "test_scores", "awards", "coursework_highlights",
    "goals_and_motivation", "summary",
}

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

    # Manual corrections always win over what re-extraction produces — a student who fixed a
    # misread GPA shouldn't see it silently revert just because they added another document.
    if profile.manual_overrides:
        structured = {**structured, **profile.manual_overrides}

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

    if doc_type in SINGLE_INSTANCE_TYPES:
        db.query(Document).filter(
            Document.profile_id == profile.id, Document.doc_type == doc_type
        ).delete()

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


@router.patch("/{profile_id}")
def update_profile(profile_id: str, payload: dict = Body(...), db: Session = Depends(get_db)):
    """Apply student-made corrections to the extracted profile. Only whitelisted fields are
    accepted; corrections are stored separately so they survive future document add/remove
    rebuilds instead of being silently overwritten by re-extraction."""
    profile = db.get(StudentProfile, profile_id)
    if not profile:
        raise HTTPException(404, "Profile not found")

    unknown = set(payload.keys()) - EDITABLE_FIELDS
    if unknown:
        raise HTTPException(400, f"Cannot edit fields: {sorted(unknown)}")

    overrides = dict(profile.manual_overrides or {})
    overrides.update(payload)
    profile.manual_overrides = overrides
    flag_modified(profile, "manual_overrides")

    structured = {**profile.structured_profile, **overrides}
    profile.structured_profile = structured
    flag_modified(profile, "structured_profile")
    db.commit()
    db.refresh(profile)

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
