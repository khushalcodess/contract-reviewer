import csv
import json
from contextlib import asynccontextmanager
from functools import partial
from pathlib import Path
from typing import Literal

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src import app_db
from src.abstain import load_thresholds
from src.bm25 import make_bm25_ranker
from src.chunking import clause_chunks
from src.db import connect, ingest_contract, make_pgvector_ranker
from src.embed import cached_chunk_embeddings
from src.hybrid import make_hybrid_ranker
from src.llm import complete
from src.loader import MAX_BYTES, UploadError, extract_text, page_for
from src.pipeline import review_contract

TAG = "clause-200-1500-200"
EVAL_DIR = Path(__file__).resolve().parent.parent / "eval"
chunker = partial(clause_chunks, max_size=1500)


@asynccontextmanager
async def lifespan(app):
    app_db.init_app_schema()
    yield


app = FastAPI(title="Contract Risk Reviewer", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def process_contract(contract_id):
    try:
        row = app_db.get_contract(contract_id, with_text=True)
        contract = {"title": row["title"], "text": row["text"]}
        chunks = chunker(contract["text"])
        with connect() as conn:
            if not app_db.has_chunks(conn, contract["title"], TAG):
                vecs = cached_chunk_embeddings(contract["title"], chunks, TAG)
                ingest_contract(conn, contract["title"], TAG, chunks, vecs)
            dense = make_pgvector_ranker(conn, TAG)
            bm25 = make_bm25_ranker(chunker)
            hybrid = make_hybrid_ranker([dense, bm25], weights=[1.0, 2.0])
            results = review_contract(contract, hybrid, {"bm25": bm25}, load_thresholds(),
                                      complete, customer=row["customer"] or None, pause=2)
        app_db.save_results(contract_id, results)
        app_db.set_status(contract_id, "done")
    except Exception as e:
        app_db.set_status(contract_id, "failed", f"{type(e).__name__}: {e}"[:500])


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/contracts")
def upload(background: BackgroundTasks, file: UploadFile = File(...), customer: str = Form("")):
    data = file.file.read(MAX_BYTES + 1)
    try:
        text, page_starts = extract_text(file.filename or "", data)
    except UploadError as e:
        raise HTTPException(status_code=400, detail=str(e))
    cid = app_db.create_contract(file.filename, text, page_starts, customer.strip() or None)
    background.add_task(process_contract, cid)
    return {"id": cid, "status": "processing"}


@app.get("/contracts")
def contracts():
    return app_db.list_contracts()


@app.get("/contracts/{cid}")
def contract(cid: int):
    meta = app_db.get_contract(cid)
    if meta is None:
        raise HTTPException(404, "Contract not found")
    meta.pop("page_starts", None)
    return meta


@app.get("/contracts/{cid}/text")
def contract_text(cid: int):
    row = app_db.get_contract(cid, with_text=True)
    if row is None:
        raise HTTPException(404, "Contract not found")
    return {"text": row["text"]}


@app.get("/contracts/{cid}/findings")
def findings(cid: int):
    meta = app_db.get_contract(cid)
    if meta is None:
        raise HTTPException(404, "Contract not found")
    out = []
    for f in app_db.get_findings(cid):
        res = f["result"]
        start = (res.get("finding") or {}).get("citation_start")
        page = page_for(start, meta["page_starts"]) if start is not None else None
        out.append({**res, "decision": f["decision"], "page": page})
    return {"status": meta["status"], "error": meta["error"], "findings": out}


class Decision(BaseModel):
    decision: Literal["accepted", "rejected", "pending"]


@app.post("/contracts/{cid}/findings/{clause}/decision")
def decide(cid: int, clause: str, body: Decision):
    if app_db.set_decision(cid, clause, body.decision) == 0:
        raise HTTPException(404, "Finding not found")
    return {"ok": True}


def _read_csv(name):
    p = EVAL_DIR / name
    if not p.exists():
        return []
    with open(p, encoding="utf-8-sig", newline="") as f:
        return [{("system" if k == "" else k): v for k, v in row.items()}
                for row in csv.DictReader(f)]


def _read_json(name):
    p = EVAL_DIR / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


@app.get("/metrics")
def metrics():
    return {"retrieval_dev": _read_csv("results_summary_dev.csv"),
            "llm_dev": _read_json("llm_eval_dev.json"),
            "llm_test": _read_json("llm_eval_test.json")}

@app.delete("/contracts/{cid}")
def remove_contract(cid: int):
    if app_db.delete_contract(cid) == 0:
        raise HTTPException(404, "Contract not found")
    return {"ok": True}