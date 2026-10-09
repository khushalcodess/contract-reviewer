import numpy as np

from src.chunking import fixed_chunks
from src.embed import cached_chunk_embeddings, embed_query
from src.queries import CLAUSE_QUERIES


def make_dense_ranker(size=1000, overlap=200):
    tag = f"fixed-{size}-{overlap}"

    def ranker(contract, clause):
        chunks = fixed_chunks(contract["text"], size, overlap)
        vecs = cached_chunk_embeddings(contract["title"], chunks, tag)
        q = embed_query(CLAUSE_QUERIES[clause])
        scores = vecs @ q
        order = np.argsort(-scores)
        return [dict(chunks[i], score=float(scores[i])) for i in order]

    return ranker