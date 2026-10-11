import re
from functools import partial

import numpy as np
from rank_bm25 import BM25Okapi

from src.chunking import clause_chunks
from src.queries import CLAUSE_KEYWORDS

TOKEN = re.compile(r"[a-z0-9]+")
STOP = {
    "the", "a", "an", "of", "to", "in", "or", "and", "by", "at", "for", "on",
    "this", "that", "is", "are", "be", "any", "with", "as", "it", "its",
}


def tokenize(text):
    return [t for t in TOKEN.findall(text.lower()) if t not in STOP]


def make_bm25_ranker(chunker=None):
    chunker = chunker or partial(clause_chunks, max_size=1500)
    cache = {}

    def ranker(contract, clause):
        title = contract["title"]
        if title not in cache:
            chunks = chunker(contract["text"])
            cache[title] = (chunks, BM25Okapi([tokenize(c["text"]) for c in chunks]))
        chunks, bm25 = cache[title]
        scores = bm25.get_scores(tokenize(CLAUSE_KEYWORDS[clause]))
        order = np.argsort(-scores)
        return [dict(chunks[i], score=float(scores[i])) for i in order]

    return ranker