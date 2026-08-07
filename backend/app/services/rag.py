"""Chunking, embedding, ingestion, and retrieval for program information (RAG)."""
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..models import ProgramChunk
from .embeddings import embed_texts, embed_text

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 150


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start = end - overlap
        if start <= 0:
            break

    filtered = [c.strip() for c in chunks if len(c.strip()) > 50]
    if filtered:
        return filtered

    # The >50-char filter exists to drop tiny meaningless fragments left over when a LARGE
    # document gets split into many pieces — it should never cause a short-but-substantive whole
    # input (e.g. a brief manual-paste fallback) to be silently discarded entirely. If filtering
    # removed everything, fall back to the original text as a single chunk when it's non-trivial.
    stripped = text.strip()
    return [stripped] if len(stripped) > 10 else []


def ingest_pages(db: Session, program_id, pages: list[dict]) -> int:
    """pages: list of {url, title, text}. Chunks, embeds, and stores them."""
    count = 0
    for page in pages:
        chunks = chunk_text(page["text"])
        if not chunks:
            continue
        vectors = embed_texts(chunks)
        for i, (chunk, vec) in enumerate(zip(chunks, vectors)):
            db.add(ProgramChunk(
                program_id=program_id,
                source_url=page["url"],
                source_title=page.get("title"),
                content=chunk,
                embedding=vec,
                chunk_index=i,
            ))
            count += 1
    db.commit()
    return count


def retrieve_relevant_chunks(db: Session, program_id, query_text: str, top_k: int = 8) -> list[ProgramChunk]:
    query_vec = embed_text(query_text)
    stmt = (
        select(ProgramChunk)
        .where(ProgramChunk.program_id == program_id)
        .order_by(ProgramChunk.embedding.cosine_distance(query_vec))
        .limit(top_k)
    )
    return list(db.execute(stmt).scalars().all())
