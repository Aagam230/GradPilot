import pytest
from app.services.pdf_extract import extract_pdf_text


def test_native_text_extraction(sample_cv_bytes):
    text = extract_pdf_text(sample_cv_bytes)
    assert "Jane Doe" in text
    assert "GPA 3.6" in text


def test_ocr_fallback_for_scanned_pdf(sample_scanned_pdf_bytes):
    """A PDF with no embedded text layer at all must still yield readable text via OCR."""
    text = extract_pdf_text(sample_scanned_pdf_bytes)
    assert "GPA" in text or "Jane" in text or "MIT" in text


def test_empty_pdf_raises():
    from reportlab.pdfgen import canvas
    import io

    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.save()  # a valid PDF with zero content
    with pytest.raises(ValueError):
        extract_pdf_text(buf.getvalue())
