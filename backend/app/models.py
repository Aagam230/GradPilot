import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    JSON,
    Integer,
    Float,
    Boolean,
)
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector

from .db import Base


EMBEDDING_DIM = 384  # sentence-transformers/all-MiniLM-L6-v2


def uuid_col():
    return Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


DOCUMENT_TYPES = (
    "cv",
    "transcript",
    "gre",
    "toefl_ielts",
    "research_paper",
    "sop",
    "other",
)


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = uuid_col()
    structured_profile = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class Document(Base):
    """
    A single uploaded document
    (CV, transcript, GRE/TOEFL score report, research paper, SOP, ...).

    A StudentProfile is the merged structured result of ALL documents
    attached to it — admissions committees judge a full application
    packet, not a resume alone.
    """

    __tablename__ = "documents"

    id = uuid_col()
    profile_id = Column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id"),
        nullable=False,
    )
    doc_type = Column(String, nullable=False)
    filename = Column(String, nullable=True)
    raw_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Program(Base):
    __tablename__ = "programs"

    id = uuid_col()
    university_name = Column(String, nullable=False)
    program_name = Column(String, nullable=False)
    seed_url = Column(String, nullable=True)
    official_domain = Column(String, nullable=True)
    structured_requirements = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ProgramChunk(Base):
    __tablename__ = "program_chunks"

    id = uuid_col()
    program_id = Column(
        UUID(as_uuid=True),
        ForeignKey("programs.id"),
        nullable=False,
    )
    source_url = Column(String, nullable=False)
    source_title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(EMBEDDING_DIM), nullable=True)
    chunk_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Analysis(Base):
    __tablename__ = "analyses"

    id = uuid_col()
    profile_id = Column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id"),
        nullable=False,
    )
    program_id = Column(
        UUID(as_uuid=True),
        ForeignKey("programs.id"),
        nullable=False,
    )
    result = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Job(Base):
    """
    Tracks an async retrieve-program + run-analysis pipeline so the
    frontend can poll status instead of holding one long HTTP request open.
    """

    __tablename__ = "jobs"

    id = uuid_col()
    status = Column(
        String,
        default="pending",
    )  # pending | retrieving | analyzing | done | error

    profile_id = Column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id"),
        nullable=False,
    )

    request_params = Column(
        JSON,
        nullable=False,
    )  # university_name, program_name, seed_url, manual_text

    program_id = Column(
        UUID(as_uuid=True),
        ForeignKey("programs.id"),
        nullable=True,
    )

    analysis_id = Column(
        UUID(as_uuid=True),
        ForeignKey("analyses.id"),
        nullable=True,
    )

    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class HistoricalApplication(Base):
    __tablename__ = "historical_applications"

    id = uuid_col()

    # Canonical program identity
    canonical_university = Column(
        String,
        nullable=False,
        index=True,
    )
    canonical_program = Column(
        String,
        nullable=False,
        index=True,
    )

    # Application information
    application_year = Column(Integer, nullable=True)
    decision = Column(
        String,
        nullable=False,
    )  # admitted / rejected / waitlisted

    # Academics
    gpa_value = Column(Float, nullable=True)
    gpa_scale = Column(Float, nullable=True)
    gpa_normalized = Column(Float, nullable=True)

    # Test scores
    gre_total = Column(Integer, nullable=True)
    gre_quant = Column(Integer, nullable=True)
    gre_verbal = Column(Integer, nullable=True)
    toefl = Column(Integer, nullable=True)
    ielts = Column(Float, nullable=True)

    # Undergraduate background
    undergraduate_major = Column(String, nullable=True)
    undergraduate_country = Column(String, nullable=True)

    # Research / experience
    research_experience = Column(Boolean, nullable=True)
    publication_count = Column(Integer, nullable=True)
    work_experience_months = Column(Integer, nullable=True)

    # Provenance
    source_type = Column(
        String,
        nullable=False,
        default="manual",
    )
    source_url = Column(String, nullable=True)
    data_quality_score = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)