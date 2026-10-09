import hashlib
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-small-en-v1.5"
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "
CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache"

_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_passages(texts, batch_size=32):
    return get_model().encode(
        texts, batch_size=batch_size, normalize_embeddings=True, show_progress_bar=False
    )


def embed_query(text):
    return get_model().encode(QUERY_PREFIX + text, normalize_embeddings=True)


def cached_chunk_embeddings(title, chunks, tag):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.md5(f"{MODEL_NAME}|{tag}|{title}".encode()).hexdigest()
    path = CACHE_DIR / f"{key}.npy"
    if path.exists():
        return np.load(path)
    vecs = embed_passages([c["text"] for c in chunks])
    np.save(path, vecs)
    return vecs