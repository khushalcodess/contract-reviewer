import os

import numpy as np
import psycopg
from pgvector.psycopg import register_vector

from src.embed import embed_query
from src.queries import CLAUSE_QUERIES

DSN = os.getenv(
    "DATABASE_URL", "postgresql://contracts:contracts_dev@localhost:5432/contracts"
)


def connect():
    conn = psycopg.connect(DSN, autocommit=True)
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    register_vector(conn)
    return conn


def init_schema(conn, dim=384):
    conn.execute("DROP TABLE IF EXISTS chunks")
    conn.execute(
        f"""
        CREATE TABLE chunks (
            id BIGSERIAL PRIMARY KEY,
            contract_title TEXT NOT NULL,
            tag TEXT NOT NULL,
            start_char INT NOT NULL,
            end_char INT NOT NULL,
            text TEXT NOT NULL,
            embedding vector({dim}) NOT NULL
        )
        """
    )
    conn.execute("CREATE INDEX chunks_contract_idx ON chunks (tag, contract_title)")


def ingest_contract(conn, title, tag, chunks, vecs):
    rows = [
        (title, tag, c["start"], c["end"], c["text"], np.asarray(v, dtype=np.float32))
        for c, v in zip(chunks, vecs)
    ]
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO chunks (contract_title, tag, start_char, end_char, text, embedding)"
            " VALUES (%s, %s, %s, %s, %s, %s)",
            rows,
        )


def search_contract(conn, title, tag, query_vec, k=1000):
    rows = conn.execute(
        """
        SELECT start_char, end_char, text, 1 - (embedding <=> %s) AS score
        FROM chunks
        WHERE tag = %s AND contract_title = %s
        ORDER BY embedding <=> %s
        LIMIT %s
        """,
        (query_vec, tag, title, query_vec, k),
    ).fetchall()
    return [
        {"start": s, "end": e, "text": t, "score": float(sc)} for s, e, t, sc in rows
    ]


def make_pgvector_ranker(conn, tag, queries=None):
    queries = queries or CLAUSE_QUERIES

    def ranker(contract, clause):
        q = embed_query(queries[clause]).astype(np.float32)
        return search_contract(conn, contract["title"], tag, q)

    return ranker