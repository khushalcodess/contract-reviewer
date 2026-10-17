import hashlib

from psycopg.types.json import Jsonb

from src.db import connect

SCHEMA = """
CREATE TABLE IF NOT EXISTS contracts (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    filename TEXT NOT NULL,
    text TEXT NOT NULL,
    page_starts JSONB,
    customer TEXT,
    status TEXT NOT NULL DEFAULT 'processing',
    error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS findings (
    id SERIAL PRIMARY KEY,
    contract_id INT NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    clause TEXT NOT NULL,
    result JSONB NOT NULL,
    decision TEXT NOT NULL DEFAULT 'pending',
    UNIQUE (contract_id, clause)
);
CREATE TABLE IF NOT EXISTS chunks (
    id BIGSERIAL PRIMARY KEY,
    contract_title TEXT NOT NULL,
    tag TEXT NOT NULL,
    start_char INT NOT NULL,
    end_char INT NOT NULL,
    text TEXT NOT NULL,
    embedding vector(384) NOT NULL
);
CREATE INDEX IF NOT EXISTS chunks_contract_idx ON chunks (tag, contract_title);
"""


def content_title(text):
    return "upload-" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def init_app_schema():
    with connect() as conn:
        conn.execute(SCHEMA)


def create_contract(filename, text, page_starts, customer):
    with connect() as conn:
        row = conn.execute(
            "INSERT INTO contracts (title, filename, text, page_starts, customer) "
            "VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (content_title(text), filename, text, Jsonb(page_starts), customer),
        ).fetchone()
    return row[0]


def set_status(contract_id, status, error=None):
    with connect() as conn:
        conn.execute("UPDATE contracts SET status = %s, error = %s WHERE id = %s",
                     (status, error, contract_id))


def get_contract(contract_id, with_text=False):
    cols = ["id", "title", "filename", "customer", "status", "error", "created_at", "page_starts"]
    if with_text:
        cols.append("text")
    with connect() as conn:
        row = conn.execute(f"SELECT {', '.join(cols)} FROM contracts WHERE id = %s",
                           (contract_id,)).fetchone()
    if row is None:
        return None
    d = dict(zip(cols, row))
    d["created_at"] = d["created_at"].isoformat()
    return d


def list_contracts(limit=50):
    with connect() as conn:
        rows = conn.execute("SELECT id, filename, status, created_at FROM contracts "
                            "ORDER BY id DESC LIMIT %s", (limit,)).fetchall()
    return [{"id": i, "filename": f, "status": s, "created_at": c.isoformat()}
            for i, f, s, c in rows]


def has_chunks(conn, title, tag):
    return conn.execute("SELECT 1 FROM chunks WHERE tag = %s AND contract_title = %s LIMIT 1",
                        (tag, title)).fetchone() is not None


def save_results(contract_id, results):
    with connect() as conn:
        for r in results:
            conn.execute(
                "INSERT INTO findings (contract_id, clause, result) VALUES (%s, %s, %s) "
                "ON CONFLICT (contract_id, clause) DO UPDATE "
                "SET result = EXCLUDED.result, decision = 'pending'",
                (contract_id, r.clause, Jsonb(r.model_dump())),
            )


def get_findings(contract_id):
    with connect() as conn:
        rows = conn.execute("SELECT clause, result, decision FROM findings "
                            "WHERE contract_id = %s ORDER BY id", (contract_id,)).fetchall()
    return [{"clause": c, "result": r, "decision": d} for c, r, d in rows]


def set_decision(contract_id, clause, decision):
    with connect() as conn:
        cur = conn.execute("UPDATE findings SET decision = %s WHERE contract_id = %s AND clause = %s",
                           (decision, contract_id, clause))
    return cur.rowcount