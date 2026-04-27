import logging
from pathlib import Path

import faiss
import numpy as np
from pypdf import PdfReader

from src.clients import google_client

logger = logging.getLogger(__name__)

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
    try:
        response = google_client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=texts,
        )
        return np.array([e.values for e in response.embeddings], dtype=np.float32)
    except Exception as e:
        logger.error("Embedding request failed: %s", e)
        raise


def load_and_index_pdfs(directory_path: str):
    global _index, _chunks
    _chunks = []

    pdf_files = list(Path(directory_path).glob("*.pdf"))
    if not pdf_files:
        logger.warning("No PDF files found in '%s'. Local retrieval will be unavailable.", directory_path)
        return

    for pdf_path in pdf_files:
        try:
            reader = PdfReader(pdf_path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            _chunks.extend(_chunk_text(text))
            logger.info("Indexed '%s' (%d chunks so far)", pdf_path.name, len(_chunks))
        except Exception as e:
            logger.error("Failed to read '%s': %s — skipping.", pdf_path.name, e)

    if not _chunks:
        logger.warning("No text could be extracted from any PDF.")
        return

    try:
        embeddings = _embed(_chunks)
        _index = faiss.IndexFlatL2(embeddings.shape[1])
        _index.add(embeddings)
        logger.info("FAISS index built with %d chunks.", len(_chunks))
    except Exception as e:
        logger.error("Failed to build FAISS index: %s", e)
        raise


def retrieve_context(query: str, top_k: int = 3) -> str:
    if _index is None or not _chunks:
        logger.info("No index available; skipping local retrieval.")
        return ""

    try:
        query_vec = _embed([query])
        _, indices = _index.search(query_vec, top_k)
        result = "\n\n---\n\n".join(_chunks[i] for i in indices[0] if i < len(_chunks))
        logger.info("Retrieved %d chunks for query.", len(indices[0]))
        return result
    except Exception as e:
        logger.error("Retrieval failed: %s", e)
        return ""
