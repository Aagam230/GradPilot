from app.services.rag import chunk_text


def test_short_substantive_text_is_not_dropped():
    """A brief manual-paste fallback (e.g. one sentence) must still become a citable chunk --
    not be silently discarded just because it's shorter than the fragment-filter threshold meant
    for splitting large documents."""
    text = "Highly selective, ~15% acceptance rate."
    result = chunk_text(text)
    assert result == [text]


def test_tiny_meaningless_text_still_dropped():
    assert chunk_text("ok") == []
    assert chunk_text("") == []


def test_long_text_still_chunks_and_filters_fragments_normally():
    text = "A" * 3000
    result = chunk_text(text)
    assert len(result) > 1
    assert all(len(c) > 50 for c in result)
