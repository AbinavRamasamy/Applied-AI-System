import os
from pathlib import Path
from pypdf import PdfReader
import numpy as np
import faiss

from src.clients import google_client, FLASH_MODEL

data_folder = Path(__file__).resolve().parent.parent/"data"

def load_and_index_pdfs(directory_path: str):
    pass

def retrieve_context(query: str, top_k: int) -> str:
    return ''
