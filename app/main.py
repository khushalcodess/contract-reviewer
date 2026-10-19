import csv
import json
import re
from contextlib import asynccontextmanager
from functools import partial
from pathlib import Path
from typing import Literal
import asyncio
import os
from fastapi import BackgroundTasks, Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src import app_db, auth
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
USER_DAILY_LIMIT = int(os.getenv("USER_DAILY_LIMIT", "5"))
GLOBAL_DAILY_LIMIT = int(os.getenv("GLOBAL_DAILY_LIMIT", "40"))
KEEP_DAYS = int(os.getenv("KEEP_DAYS", "7"))

async def _cleanup_loop():
    while True:
        try:
            await asyncio.to_thread(app_db.delete_old_contracts, KEEP_DAYS)
        except Exception as e:
            print("cleanup failed:", e)
        await asyncio.sleep(3600)


@asynccontextmanager
async def lifespan(app):
    app_db.init_app_schema()
    task = asyncio.create_task(_cleanup_loop())
    yield
    task.cancel()


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


# ---------- auth ----------

class Credentials(BaseModel):
    email: str
    password: str


def _clean_email(email):
    email = email.strip().lower()
    if len(email) > 254 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise HTTPException(400, "Enter a valid email")
    return email


@app.post("/auth/signup")
def signup(body: Credentials):
    email = _clean_email(body.email)
    if not 8 <= len(body.password) <= 128:
        raise HTTPException(400, "Password must be 8 to 128 characters")
    uid = app_db.create_user(email, auth.hash_password(body.password))
    if uid is None:
        raise HTTPException(409, "This email is already registered")
    return {"token": auth.make_token(uid)}


@app.post("/auth/login")
def login(body: Credentials):
    row = app_db.get_user_by_email(body.email.strip().lower())
    if row is None or not auth.verify_password(body.password, row[1]):
        raise HTTPException(401, "Wrong email or password")
    return {"token": auth.make_token(row[0])}


def current_user(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Please log in")
    uid = auth.read_token(authorization[7:])
    if uid is None:
        raise HTTPException(401, "Please log in again")
    return uid


def own(cid, uid):
    if app_db.contract_owner(cid) != uid:
        raise HTTPException(404, "Contract not found")


# ---------- contracts ----------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/contracts")
def upload(background: BackgroundTasks, file: UploadFile = File(...),
           customer: str = Form(""), uid: int = Depends(current_user)):
    if app_db.count_uploads(uid) >= USER_DAILY_LIMIT:
        raise HTTPException(429, f"Daily limit reached ({USER_DAILY_LIMIT} uploads per day). Try again tomorrow.")
    if app_db.count_uploads() >= GLOBAL_DAILY_LIMIT:
        raise HTTPException(429, "The demo has reached its daily limit. Please try again tomorrow.")

    data = file.file.read(MAX_BYTES + 1)
    try:
        text, page_starts = extract_text(file.filename or "", data)
    except UploadError as e:
        raise HTTPException(status_code=400, detail=str(e))
    cid = app_db.create_contract(file.filename, text, page_starts,
                                 customer.strip() or None, uid)
    background.add_task(process_contract, cid)
    return {"id": cid, "status": "processing"}


@app.get("/contracts")
def contracts(uid: int = Depends(current_user)):
    return app_db.list_contracts(uid)


@app.get("/contracts/{cid}")
def contract(cid: int, uid: int = Depends(current_user)):
    own(cid, uid)
    meta = app_db.get_contract(cid)
    meta.pop("page_starts", None)
    return meta


@app.get("/contracts/{cid}/text")
def contract_text(cid: int, uid: int = Depends(current_user)):
    own(cid, uid)
    return {"text": app_db.get_contract(cid, with_text=True)["text"]}


@app.delete("/contracts/{cid}")
def remove_contract(cid: int, uid: int = Depends(current_user)):
    own(cid, uid)
    app_db.delete_contract(cid)
    return {"ok": True}


@app.get("/contracts/{cid}/findings")
def findings(cid: int, uid: int = Depends(current_user)):
    own(cid, uid)
    meta = app_db.get_contract(cid)
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
def decide(cid: int, clause: str, body: Decision, uid: int = Depends(current_user)):
    own(cid, uid)
    if app_db.set_decision(cid, clause, body.decision) == 0:
        raise HTTPException(404, "Finding not found")
    return {"ok": True}


# ---------- metrics (result files only, no contract data) ----------

def _read_json(name):
    p = EVAL_DIR / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _retrieval(split):
    out = []
    for p in sorted(EVAL_DIR.glob(f"results_*_{split}.csv")):
        name = p.stem[len("results_"):-len(f"_{split}")]
        if name == "summary":
            continue
        with open(p, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            continue
        try:
            vals = {k: [float(r[k]) for r in rows] for k in ("hit@1", "hit@3", "mrr")}
        except (KeyError, ValueError):
            continue
        out.append({"system": name, "clauses": len(rows),
                    **{k: round(sum(v) / len(v), 3) for k, v in vals.items()}})
    return out


@app.get("/metrics")
def metrics():
    return {"retrieval_dev": _retrieval("dev"),
            "retrieval_test": _retrieval("test"),
            "llm_dev": _read_json("llm_eval_dev.json"),
            "llm_test": _read_json("llm_eval_test.json")}