import json
from pathlib import Path

from src.abstain import clause_is_present

PATH = Path(__file__).resolve().parent.parent / "eval" / "thresholds.json"
GATED = {"Governing Law", "Cap On Liability"}


def _load():
    return json.loads(PATH.read_text(encoding="utf-8-sig"))


def test_only_two_clauses_are_gated():
    for clause, rule in _load().items():
        if clause in GATED:
            assert rule["signal"] == "bm25"
        else:
            assert rule["signal"] is None


def test_ungated_clause_is_never_rejected_by_gate():
    data = _load()
    for clause in data:
        if clause not in GATED:
            assert clause_is_present(clause, {}, data) is True