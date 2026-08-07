"""Extract raw text from an uploaded PDF. Treated as untrusted data, never instructions.

Falls back to OCR (tesseract via pdf2image) for scanned/image-only PDFs where no embedded
text layer exists — common for scanned transcripts and official score reports.
Requires system packages: tesseract-ocr, poppler-utils.
"""
import io
from pypdf import PdfReader

MIN_TEXT_LENGTH = 40  # below this, treat as "no usable text layer" and try OCR


def _extract_native_text(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def _extract_via_ocr(file_bytes: bytes) -> str:
    from pdf2image import convert_from_bytes
    import pytesseract

    images = convert_from_bytes(file_bytes, dpi=200)
    pages = [pytesseract.image_to_string(img) for img in images]
    return "\n".join(pages).strip()


def extract_pdf_text(file_bytes: bytes) -> str:
    text = _extract_native_text(file_bytes)
    if len(text) >= MIN_TEXT_LENGTH:
        return text

    try:
        ocr_text = _extract_via_ocr(file_bytes)
    except Exception as e:
        raise ValueError(
            f"Could not extract text from PDF, and OCR fallback failed ({e}). "
            "The file may be corrupted or password-protected."
        )

    if len(ocr_text) < MIN_TEXT_LENGTH:
        raise ValueError(
            "Could not extract any readable text from this PDF, even with OCR. "
            "It may be blank, corrupted, or too low-resolution to read."
        )
    return ocr_text
