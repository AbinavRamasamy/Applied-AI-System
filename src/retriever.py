import os
from pathlib import Path
from pypdf import PdfReader
import numpy as np
import faiss

from src.clients import google_client

data_folder = Path(__file__).resolve().parent.parent / "data"

EMBEDDING_MODEL = "text-embedding-004"
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50

_index: faiss.IndexFlatL2 | None = None
_chunks: list[str] = []


def _chunk_text(text: str) -> list[str]:
    words = text.split()
    step = CHUNK_SIZE - CHUNK_OVERLAP
    return [
        " ".join(words[i : i + CHUNK_SIZE])
        for i in range(0, len(words), step)
        if words[i : i + CHUNK_SIZE]
    ]


def _embed(texts: list[str]) -> np.ndarray:
    response = google_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
    )
    return np.array([e.values for e in response.embeddings], dtype=np.float32)


def load_and_index_pdfs(directory_path: str):
    global _index, _chunks
    _chunks = []

    for pdf_path in Path(directory_path).glob("*.pdf"):
        reader = PdfReader(pdf_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        _chunks.extend(_chunk_text(text))

    if not _chunks:
        return

    embeddings = _embed(_chunks)
    _index = faiss.IndexFlatL2(embeddings.shape[1])
    _index.add(embeddings)


def retrieve_context(query: str, top_k: int = 3) -> str:
    if _index is None or not _chunks:
        return ""

    query_vec = _embed([query])
    _, indices = _index.search(query_vec, top_k)
    return "\n\n---\n\n".join(_chunks[i] for i in indices[0] if i < len(_chunks))
