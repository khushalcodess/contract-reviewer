from src.hybrid import rrf_fuse

A = {"start": 0, "end": 10}
B = {"start": 10, "end": 20}
C = {"start": 20, "end": 30}


def test_chunk_ranked_high_by_both_wins():
    fused = rrf_fuse([[A, B, C], [B, C, A]])
    assert (fused[0]["start"], fused[0]["end"]) == (10, 20)


def test_union_of_chunks():
    assert len(rrf_fuse([[A, B], [C]])) == 3


def test_zero_weight_ignores_second_list():
    fused = rrf_fuse([[A, B, C], [C, B, A]], weights=[1.0, 0.0])
    assert [f["start"] for f in fused] == [0, 10, 20]