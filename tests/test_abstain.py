from src.abstain import pick_threshold, clause_is_present


def test_pick_threshold_keeps_target_share():
    scores = list(range(1, 101))
    t = pick_threshold(scores, 0.90)
    assert sum(s >= t for s in scores) >= 90


def test_clause_is_present():
    th = {"Governing Law": {"signal": "dense_kw", "threshold": 0.6}}
    assert clause_is_present("Governing Law", {"dense_kw": 0.7}, th)
    assert not clause_is_present("Governing Law", {"dense_kw": 0.5}, th)