def _overlap(chunk, span):
    s, e = span
    return chunk["start"] < e and s < chunk["end"]


def hit_at_k(ranked, gold, k):
    return float(any(_overlap(ch, sp) for ch in ranked[:k] for sp in gold))


def span_recall_at_k(ranked, gold, k):
    covered = sum(any(_overlap(ch, sp) for ch in ranked[:k]) for sp in gold)
    return covered / len(gold)


def reciprocal_rank(ranked, gold):
    for i, ch in enumerate(ranked, start=1):
        if any(_overlap(ch, sp) for sp in gold):
            return 1.0 / i
    return 0.0


def evaluate_ranker(ranker, contracts, indices, clause, ks=(1, 3, 5, 10)):
    scores = {f"hit@{k}": [] for k in ks}
    scores.update({f"span_recall@{k}": [] for k in ks})
    scores["mrr"] = []

    for i in indices:
        c = contracts[i]
        gold = c["gold"][clause]
        if not gold:
            continue
        ranked = ranker(c, clause)
        for k in ks:
            scores[f"hit@{k}"].append(hit_at_k(ranked, gold, k))
            scores[f"span_recall@{k}"].append(span_recall_at_k(ranked, gold, k))
        scores["mrr"].append(reciprocal_rank(ranked, gold))

    n = len(scores["mrr"])
    result = {name: round(sum(v) / n, 3) for name, v in scores.items()}
    result["n"] = n
    return result