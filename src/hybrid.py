def rrf_fuse(rankings, k=60, weights=None):
    weights = weights or [1.0] * len(rankings)
    fused = {}
    for w, ranked in zip(weights, rankings):
        for rank, ch in enumerate(ranked, start=1):
            key = (ch["start"], ch["end"])
            if key not in fused:
                fused[key] = {"chunk": ch, "score": 0.0}
            fused[key]["score"] += w / (k + rank)
    out = sorted(fused.values(), key=lambda x: -x["score"])
    return [dict(o["chunk"], score=o["score"]) for o in out]


def make_hybrid_ranker(rankers, k=60, weights=None):
    def ranker(contract, clause):
        return rrf_fuse([r(contract, clause) for r in rankers], k, weights)

    return ranker