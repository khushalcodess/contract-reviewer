import math

LEVELS = ["Low", "Medium", "High"]


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((centre - margin) / denom, (centre + margin) / denom)


def _rate(k, n):
    lo, hi = wilson(k, n)
    return {"k": k, "n": n, "rate": round(k / n, 3) if n else None,
            "ci95": [round(lo, 3), round(hi, 3)]}


def score_items(rows):
    labeled = [r for r in rows if r["label"] in LEVELS]
    found = [r for r in labeled if r["status"] == "found"]
    correct = [r for r in found if r["pred_risk"] == r["label"]]
    within_one = [r for r in found
                  if abs(LEVELS.index(r["pred_risk"]) - LEVELS.index(r["label"])) <= 1]
    unverified = [r for r in labeled if r["status"] == "unverified"]
    called = [r for r in labeled if r.get("llm_calls", 0) > 0]
    retried = [r for r in called if r["llm_calls"] > 1]
    overlapping = [r for r in found if r.get("overlap")]

    confusion = {}
    for r in labeled:
        pred = r["pred_risk"] if r["status"] == "found" else r["status"]
        confusion.setdefault(r["label"], {})
        confusion[r["label"]][pred] = confusion[r["label"]].get(pred, 0) + 1

    return {
        "items_total": len(rows),
        "items_labeled": len(labeled),
        "items_marked_NA": len(rows) - len(labeled),
        "found_rate": _rate(len(found), len(labeled)),
        "risk_accuracy": _rate(len(correct), len(labeled)),
        "accuracy_when_found": _rate(len(correct), len(found)),
        "within_one_level_when_found": _rate(len(within_one), len(found)),
        "unverified_rate": _rate(len(unverified), len(labeled)),
        "first_try_failure_rate": _rate(len(retried), len(called)),
        "citation_overlaps_lawyer_span": _rate(len(overlapping), len(found)),
        "confusion": confusion,
    }


def score_absent(rows):
    def found(sub):
        return sum(r["status"] == "found" for r in sub)

    out = {"overall": _rate(found(rows), len(rows)),
           "blocked_by_gate": sum(r["decided_by"] == "gate" for r in rows),
           "by_clause": {}}
    for clause in sorted({r["clause"] for r in rows}):
        sub = [r for r in rows if r["clause"] == clause]
        out["by_clause"][clause] = _rate(found(sub), len(sub))
    return out
