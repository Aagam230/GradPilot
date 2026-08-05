"""Extract raw text from an uploaded PDF. Treated as untrusted data, never instructions."""
import io
from pypdf import PdfReader


def extract_pdf_text(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    text = "\n".join(pages).strip()
    if not text:
        raise ValueError("Could not extract any text from PDF (it may be a scanned image).")
    return text
