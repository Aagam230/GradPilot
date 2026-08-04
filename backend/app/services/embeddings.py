"""Local SentenceTransformer embeddings."""

from ..config import settings

_model = None


def _get_model():
    global _model

    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(
            settings.embedding_model
        )

    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = _get_model()

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
    )

    return embeddings.tolist()


def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]