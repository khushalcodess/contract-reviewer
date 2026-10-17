from src.eval_llm import score_absent, score_items, wilson


def row(label, status, pred=None, calls=1, overlap=True):
    return {"label": label, "status": status, "pred_risk": pred,
            "llm_calls": calls, "overlap": overlap}


def test_wilson_basics():
    assert wilson(0, 0) == (0.0, 0.0)
    lo, hi = wilson(5, 10)
    assert 0 < lo < 0.5 < hi < 1
    assert abs(wilson(10, 10)[1] - 1.0) < 1e-9


def test_score_items_counts():
    rows = [row("High", "found", "High"), row("Medium", "found", "High", calls=2),
            row("Low", "not_found"), row("NA", "found", "Low")]
    s = score_items(rows)
    assert s["items_labeled"] == 3 and s["items_marked_NA"] == 1
    assert (s["risk_accuracy"]["k"], s["risk_accuracy"]["n"]) == (1, 3)
    assert s["accuracy_when_found"]["n"] == 2
    assert s["within_one_level_when_found"]["k"] == 2
    assert (s["first_try_failure_rate"]["k"], s["first_try_failure_rate"]["n"]) == (1, 3)
    assert s["confusion"]["Medium"] == {"High": 1}
    assert s["confusion"]["Low"] == {"not_found": 1}


def test_score_absent():
    rows = [{"clause": "A", "status": "found", "decided_by": "llm"},
            {"clause": "A", "status": "not_found", "decided_by": "gate"},
            {"clause": "B", "status": "not_found", "decided_by": "llm"}]
    s = score_absent(rows)
    assert (s["overall"]["k"], s["overall"]["n"]) == (1, 3)
    assert s["by_clause"]["A"]["n"] == 2 and s["blocked_by_gate"] == 1
