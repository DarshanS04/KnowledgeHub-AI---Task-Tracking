import pytest
from app.utils.text_processing import clean_text, TokenBasedTextSplitter


def test_clean_text():
    # Test whitespace stripping and unicode normalization
    raw = "Hello   world! \n\n\n This is a \t test.\x00"
    cleaned = clean_text(raw)
    assert "  " not in cleaned
    assert "\x00" not in cleaned
    assert cleaned.startswith("Hello world!")
    assert "This is a test." in cleaned


def test_splitter_chunks():
    splitter = TokenBasedTextSplitter(chunk_size=100, chunk_overlap=10)
    # Long text to force splits
    text = (
        "This is a very long text designed to verify that the RecursiveCharacterTextSplitter "
        "class partitions content correctly. It splits by paragraphs, sentences, and words. "
        "Each chunk should fit within the configured size threshold, preserving semantic structure."
    )
    chunks = splitter.split(text)
    assert len(chunks) > 0
    # Every chunk should be cleaned and have content
    for chunk in chunks:
        assert len(chunk) <= 100
        assert len(chunk) > 0
