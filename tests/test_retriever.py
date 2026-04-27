from unittest.mock import MagicMock, patch

import numpy as np
import pytest

import src.retriever as retriever


# --- _chunk_text (pure function) ---

def test_chunk_text_returns_chunks():
    words = ["word"] * 500
    chunks = retriever._chunk_text(" ".join(words))
    assert len(chunks) > 1
    assert all(isinstance(c, str) for c in chunks)


def test_chunk_text_empty_string():
    assert retriever._chunk_text("") == []


def test_chunk_text_short_text():
    text = "hello world"
    chunks = retriever._chunk_text(text)
    assert len(chunks) == 1
    assert chunks[0] == "hello world"


# --- retrieve_context with no index ---

def test_retrieve_context_returns_empty_when_no_index(monkeypatch):
    monkeypatch.setattr(retriever, "_index", None)
    monkeypatch.setattr(retriever, "_chunks", [])
    assert retriever.retrieve_context("anything") == ""


# --- load_and_index_pdfs ---

def test_load_no_pdfs_does_not_crash(tmp_path):
    # Empty directory — should log a warning and return without raising.
    retriever.load_and_index_pdfs(str(tmp_path))


def test_load_and_index_pdfs_indexes_text(tmp_path, monkeypatch):
    # Create a fake PDF file so glob finds it.
    fake_pdf = tmp_path / "doc.pdf"
    fake_pdf.write_bytes(b"fake")

    fake_page = MagicMock()
    fake_page.extract_text.return_value = "alpha beta gamma " * 50

    fake_reader = MagicMock()
    fake_reader.pages = [fake_page]

    fake_embeddings = np.random.rand(10, 768).astype(np.float32)

    with patch("src.retriever.PdfReader", return_value=fake_reader), \
         patch("src.retriever._embed", return_value=fake_embeddings):
        retriever.load_and_index_pdfs(str(tmp_path))

    assert len(retriever._chunks) > 0
    assert retriever._index is not None


def test_bad_pdf_is_skipped(tmp_path, monkeypatch):
    bad_pdf = tmp_path / "bad.pdf"
    bad_pdf.write_bytes(b"not a pdf")

    with patch("src.retriever.PdfReader", side_effect=Exception("corrupt")):
        # Should not raise; bad file is skipped.
        retriever.load_and_index_pdfs(str(tmp_path))
