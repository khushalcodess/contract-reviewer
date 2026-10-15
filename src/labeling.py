import csv
import json
import random
import re
from pathlib import Path

from src.data import TARGET_CLAUSES, load_cuad

ROOT = Path(__file__).resolve().parent.parent
SPLIT = ROOT / "eval" / "split.json"
OUT = ROOT / "eval" / "label_set.csv"
PER_CLAUSE = 5
MAX_CHARS = 1500


def dev_contracts(contracts):
    split = json.loads(SPLIT.read_text(encoding="utf-8-sig"))
    dev = split["dev"]
    if dev and isinstance(dev[0], int):
        return [contracts[i] for i in dev]
    titles = set(dev)
    return [c for c in contracts if c["title"] in titles]


def indemnity_paragraph(text):
    for para in re.split(r"\n\s*\n", text):
        if re.search(r"indemnif", para, re.I) and 150 < len(para) < MAX_CHARS:
            return para.strip()
    return None


def main():
    if OUT.exists():
        raise SystemExit(f"{OUT} already exists. Not overwriting your labels.")
    rng = random.Random(42)
    dev = dev_contracts(load_cuad())
    rows = []

    for clause in TARGET_CLAUSES:
        pool = [c for c in dev if c["gold"].get(clause)]
        rng.shuffle(pool)
        for c in pool[:PER_CLAUSE]:
            s, e = c["gold"][clause][0]
            rows.append([c["title"], clause, c["text"][s:e][:MAX_CHARS]])

    pool = list(dev)
    rng.shuffle(pool)
    n = 0
    for c in pool:
        para = indemnity_paragraph(c["text"])
        if para:
            rows.append([c["title"], "Indemnification", para])
            n += 1
        if n == PER_CLAUSE:
            break

    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id", "title", "clause", "text", "risk", "reason"])
        for i, r in enumerate(rows, 1):
            w.writerow([i] + r + ["", ""])
    print(f"wrote {len(rows)} rows to {OUT}")


if __name__ == "__main__":
    main()