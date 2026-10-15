import hashlib
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

BASE_URL = os.getenv("LLM_BASE_URL")
API_KEY = os.getenv("LLM_API_KEY")
MODEL = os.getenv("LLM_MODEL")

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "data" / "cache" / "llm"
LOG_PATH = ROOT / "data" / "cache" / "llm_calls.jsonl"

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(
            base_url=BASE_URL,
            api_key=API_KEY,
            timeout=60,
            max_retries=2,
        )
    return _client


def _cache_key(system, user, max_tokens):
    raw = json.dumps([MODEL, system, user, max_tokens], ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _log(record):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def complete(system, user, max_tokens=1000, use_cache=True):
    key = _cache_key(system, user, max_tokens)
    path = CACHE_DIR / f"{key}.json"

    if use_cache and path.exists():
        reply = json.loads(path.read_text(encoding="utf-8"))["reply"]
        _log({"time": time.time(), "model": MODEL, "cached": True,
              "latency_s": 0.0, "prompt_tokens": 0, "completion_tokens": 0})
        return reply

    start = time.time()
    resp = _get_client().chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        temperature=0.0,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    latency = time.time() - start
    reply = resp.choices[0].message.content or ""

    usage = getattr(resp, "usage", None)
    _log({
        "time": time.time(), "model": MODEL, "cached": False,
        "latency_s": round(latency, 2),
        "prompt_tokens": getattr(usage, "prompt_tokens", None),
        "completion_tokens": getattr(usage, "completion_tokens", None),
    })

    if use_cache and reply:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"model": MODEL, "reply": reply}),
                        encoding="utf-8")
    return reply