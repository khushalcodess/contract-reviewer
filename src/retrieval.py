import numpy as np

from src.chunking import fixed_chunks
from src.embed import cached_chunk_embeddings, embed_query
from src.queries import CLAUSE_QUERIES


def make_dense_ranker(chunker=None, tag="fixed-1000-200", queries=None):
    chunker = chunker or fixed_chunks
    queries = queries or CLAUSE_QUERIES

    def ranker(contract, clause):
        chunks = chunker(contract["text"])
        vecs = cached_chunk_embeddings(contract["title"], chunks, tag)
        q = embed_query(queries[clause])
        scores = vecs @ q
        order = np.argsort(-scores)
        return [dict(chunks[i], score=float(scores[i])) for i in order]

    return ranker