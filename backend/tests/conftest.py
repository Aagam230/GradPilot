"""Shared test fixtures.

IMPORTANT: env vars must be set before `app.*` is imported anywhere, because app/config.py and
app/db.py bind to them at import time (including inside background-task code in
services/pipeline.py, which creates its own DB session directly rather than via FastAPI's
dependency-injection — so there's no per-request override that would catch it; the whole process
must be pointed at the test database via env var instead).

Run tests against a DEDICATED test database, never the dev one:
    createdb gradpilot_test  (or: psql -c "CREATE DATABASE gradpilot_test OWNER gradpilot;")
    psql -d gradpilot_test -c "CREATE EXTENSION IF NOT EXISTS vector;"
"""
import io
import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault(
    "DATABASE_URL", "postgresql+psycopg2://gradpilot:gradpilot@localhost:5432/gradpilot_test"
)
os.environ.setdefault("ANTHROPIC_API_KEY", "test")
os.environ.setdefault("OPENAI_API_KEY", "test")
os.environ.setdefault("TAVILY_API_KEY", "")

import pytest
from sqlalchemy import text
from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(autouse=True)
def _clean_tables():
    """Every test starts with empty tables — tests must not depend on execution order or leak
    state into each other (a lesson learned the hard way earlier in this project's history, when
    manual test scripts gave misleading results due to stale data from a previous run)."""
    yield
    with engine.connect() as conn:
        conn.execute(text(
            "TRUNCATE analyses, program_chunks, programs, documents, student_profiles, jobs "
            "RESTART IDENTITY CASCADE"
        ))
        conn.commit()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_cv_bytes() -> bytes:
    """A simple text-layer PDF — exercises the native pypdf extraction path."""
    from reportlab.pdfgen import canvas

    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    lines = [
        "Jane Doe",
        "Education: BSc Computer Science, MIT, GPA 3.6, 2020-2024",
        "Research Experience: Reinforcement learning for robotics, MIT AI Lab, 1 year",
        "Projects: Distributed key-value store in Go",
        "Work Experience: Software Engineer Intern, Google, Summer 2023",
        "Skills: Python, PyTorch, C++",
        "Test Scores: GRE 314",
        "Awards: Dean's List 2022",
    ]
    y = 800
    for line in lines:
        c.drawString(50, y, line)
        y -= 20
    c.save()
    return buf.getvalue()


@pytest.fixture
def sample_scanned_pdf_bytes() -> bytes:
    """An image-only PDF with NO embedded text layer — exercises the OCR fallback path."""
    from PIL import Image, ImageDraw
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader

    img = Image.new("RGB", (1000, 300), color="white")
    draw = ImageDraw.Draw(img)
    lines = ["OFFICIAL TRANSCRIPT", "Jane Doe", "Cumulative GPA: 3.85", "Institution: MIT"]
    y = 20
    for line in lines:
        draw.text((20, y), line, fill="black")
        y += 40
    img_buf = io.BytesIO()
    img.save(img_buf, format="PNG")
    img_buf.seek(0)

    pdf_buf = io.BytesIO()
    c = canvas.Canvas(pdf_buf)
    c.drawImage(ImageReader(img_buf), 50, 400, width=500, height=150)
    c.save()
    return pdf_buf.getvalue()


def fake_profile_extraction(**overrides) -> dict:
    """Baseline fake structured-profile response, overridable per test."""
    base = {
        "name": "Jane Doe",
        "education": [{"degree": "BSc", "field": "CS", "institution": "MIT", "gpa": "3.6", "years": "2020-2024"}],
        "research_experience": [],
        "projects": [],
        "work_experience": [],
        "publications": [],
        "skills": ["Python"],
        "test_scores": [{"test": "GRE", "score": "314"}],
        "awards": [],
        "coursework_highlights": [],
        "goals_and_motivation": None,
        "summary": "CS student.",
    }
    base.update(overrides)
    return base


def fake_embed_texts(texts: list[str]) -> list[list[float]]:
    import random
    return [[random.random() for _ in range(384)] for _ in texts]
