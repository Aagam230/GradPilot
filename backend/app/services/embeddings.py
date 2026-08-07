"""Local MiniLM embeddings (384 dimensions), matching the GradPilot pgvector schema."""
from functools import lru_cache
from ..config import settings


@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    if settings.embedding_provider != "sentence_transformers":
        raise ValueError(f"Unknown EMBEDDING_PROVIDER: {settings.embedding_provider}")
    if not texts:
        return []
    vectors = _model().encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return vectors.tolist()


def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]
