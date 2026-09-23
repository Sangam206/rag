import pytest
from app.services.chunking_service import chunk_text


def test_fixed_size_splits_text():
    text = "Hello world. " * 200
    chunks = chunk_text(text, strategy="fixed_size", chunk_size=500, overlap=50)
    assert len(chunks) > 1


def test_fixed_size_respects_limit():
    text = "A" * 1500
    chunks = chunk_text(text, strategy="fixed_size", chunk_size=500, overlap=50)
    for chunk in chunks:
        assert len(chunk) <= 500


def test_fixed_size_overlap_works():
    text = "A" * 1000
    with_overlap = chunk_text(text, strategy="fixed_size", chunk_size=500, overlap=100)
    without_overlap = chunk_text(text, strategy="fixed_size", chunk_size=500, overlap=0)
    assert len(with_overlap) >= len(without_overlap)


def test_fixed_size_short_text():
    chunks = chunk_text("Short text.", strategy="fixed_size", chunk_size=500)
    assert len(chunks) == 1


def test_recursive_splits_paragraphs():
    text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
    chunks = chunk_text(text, strategy="recursive", chunk_size=1000)
    assert len(chunks) >= 1


def test_recursive_handles_big_paragraphs():
    text = "A" * 600 + "\n\n" + "B" * 600
    chunks = chunk_text(text, strategy="recursive", chunk_size=500)
    assert len(chunks) >= 2


def test_empty_text_returns_nothing():
    assert chunk_text("", strategy="fixed_size") == []
    assert chunk_text("", strategy="recursive") == []


def test_bad_strategy_raises_error():
    with pytest.raises(ValueError):
        chunk_text("hello", strategy="unknown")
