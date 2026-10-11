import hashlib
import json
from pathlib import Path

from sentence_transformers import CrossEncoder

from src.queries import CLAUSE_QUERIES

RERANK_MODEL = "BAAI/bge-reranker-base"
CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "rerank_cache"

_model = None


def get_reranker():
    global _model
    if _model is None:
        _model = CrossEncoder(RERANK_MODEL, max_length=512)
    return _model


def make_rerank_ranker(base_ranker, top_n=10, model_name=RERANK_MODEL):
    def ranker(contract, clause):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        ranked = base_ranker(contract, clause)
        head, tail = ranked[:top_n], ranked[top_n:]

        spans = [(c["start"], c["end"]) for c in head]
        key = hashlib.md5(
            f"{model_name}|{top_n}|{contract['title']}|{clause}|{spans}".encode()
        ).hexdigest()
        path = CACHE_DIR / f"{key}.json"

        if path.exists():
            scores = json.loads(path.read_text())
        else:
            pairs = [(CLAUSE_QUERIES[clause], c["text"]) for c in head]
            scores = [float(s) for s in get_reranker().predict(pairs, batch_size=16)]
            path.write_text(json.dumps(scores))

        order = sorted(range(len(head)), key=lambda i: -scores[i])
        return [dict(head[i], score=scores[i]) for i in order] + tail

    return ranker