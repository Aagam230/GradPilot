"""Local sentence-transformer embeddings for GradPilot."""
from functools import lru_cache
from ..config import settings


@lru_cache(maxsize=1)
def _model():
    if settings.embedding_provider != "local":
        raise ValueError(f"Unknown EMBEDDING_PROVIDER: {settings.embedding_provider}")
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    vectors = _model().encode(texts, normalize_embeddings=True)
    return vectors.tolist()


def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]
