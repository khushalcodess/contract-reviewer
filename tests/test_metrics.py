from src.metrics import hit_at_k, span_recall_at_k, reciprocal_rank

chunks = [
    {"start": 0, "end": 100},
    {"start": 100, "end": 200},
    {"start": 200, "end": 300},
]


def test_hit_found_at_rank_2():
    gold = [(150, 180)]
    assert hit_at_k(chunks, gold, 1) == 0.0
    assert hit_at_k(chunks, gold, 2) == 1.0


def test_touching_edges_do_not_count():
    assert hit_at_k(chunks, [(100, 110)], 1) == 0.0


def test_span_recall_partial():
    gold = [(10, 20), (250, 260)]
    assert span_recall_at_k(chunks, gold, 1) == 0.5
    assert span_recall_at_k(chunks, gold, 3) == 1.0


def test_reciprocal_rank():
    assert reciprocal_rank(chunks, [(210, 220)]) == 1 / 3
    assert reciprocal_rank(chunks, [(900, 910)]) == 0.0