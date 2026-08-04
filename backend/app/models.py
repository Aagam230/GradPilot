import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from .db import Base

EMBEDDING_DIM = 384 # matches text-embedding-3-small; change if embedding model changes


def uuid_col():
    return Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class StudentProfile(Base):
    __tablename__ = "student_profiles"
    id = uuid_col()
    raw_text = Column(Text, nullable=False)
    structured_profile = Column(JSON, nullable=False)
    source_filename = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Program(Base):
    __tablename__ = "programs"
    id = uuid_col()
    university_name = Column(String, nullable=False)
    program_name = Column(String, nullable=False)
    seed_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ProgramChunk(Base):
    __tablename__ = "program_chunks"
    id = uuid_col()
    program_id = Column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=False)
    source_url = Column(String, nullable=False)
    source_title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(EMBEDDING_DIM), nullable=True)
    chunk_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Analysis(Base):
    __tablename__ = "analyses"
    id = uuid_col()
    profile_id = Column(UUID(as_uuid=True), ForeignKey("student_profiles.id"), nullable=False)
    program_id = Column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=False)
    result = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
