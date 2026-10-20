import csv
import json
import random
import re
import sys
from pathlib import Path

from src.data import CUAD_PATH, TARGET_CLAUSES, load_cuad

ROOT = Path(__file__).resolve().parent.parent
SPLIT = ROOT / "eval" / "split.json"
PER_CLAUSE = 6
MAX_CHARS = 1500
MIN_CHARS = 40
PAD = 400
FIELDS = ["id", "title", "parties", "clause", "text", "start", "end",
          "customer", "risk", "reason", "unsure"]


def out_path(split_name):
    return ROOT / "eval" / ("label_set.csv" if split_name == "dev" else f"label_set_{split_name}.csv")


def contracts_in(split_name, contracts):
    titles = set(json.loads(SPLIT.read_text(encoding="utf-8-sig"))[split_name])
    return [c for c in contracts if c["title"] in titles]


def parties_by_title():
    raw = json.loads(CUAD_PATH.read_text(encoding="utf-8"))
    out = {}
    for c in raw["data"]:
        for qa in c["paragraphs"][0]["qas"]:
            if qa["id"].endswith("Parties"):
                names = [a["text"].strip() for a in qa["answers"]]
                out[c["title"]] = " | ".join(names)[:200]
    return out


def with_context(text, s, e, pad=PAD):
    e = min(e, s + MAX_CHARS)
    a, b = max(0, s - pad), min(len(text), e + pad)
    return text[a:s] + ">>> " + text[s:e] + " <<<" + text[e:b]


def paragraphs(text):
    pos = 0
    for m in re.finditer(r"\n\s*\n", text):
        yield pos, text[pos:m.start()]
        pos = m.end()
    yield pos, text[pos:]


def indemnity_paragraph(text):
    for pos, para in paragraphs(text):
        if re.search(r"indemnif", para, re.I) and 150 < len(para) < MAX_CHARS:
            return pos, pos + len(para), para
    return None


def main(split_name="dev"):
    out = out_path(split_name)
    if out.exists():
        raise SystemExit(f"{out.name} already exists. Not overwriting, your labels may be inside.")

    rng = random.Random(42)
    pool_all = contracts_in(split_name, load_cuad())
    parties = parties_by_title()
    rows = []

    for clause in TARGET_CLAUSES:
        pool = [c for c in pool_all
                if any(e - s >= MIN_CHARS for s, e in c["gold"].get(clause, []))]
        rng.shuffle(pool)
        for c in pool[:PER_CLAUSE]:
            s, e = next((s, e) for s, e in c["gold"][clause] if e - s >= MIN_CHARS)
            rows.append([c["title"], parties.get(c["title"], ""), clause,
                         with_context(c["text"], s, e), s, e])

    pool = list(pool_all)
    rng.shuffle(pool)
    n = 0
    for c in pool:
        hit = indemnity_paragraph(c["text"])
        if hit:
            s, e, para = hit
            rows.append([c["title"], parties.get(c["title"], ""), "Indemnification", para, s, e])
            n += 1
        if n == PER_CLAUSE:
            break

    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(FIELDS)
        for i, r in enumerate(rows, 1):
            w.writerow([i] + r + ["", "", "", ""])
    print(f"wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "dev")