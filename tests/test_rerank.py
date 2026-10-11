from src import rerank


class FakeModel:
    def predict(self, pairs, batch_size=16):
        return [len(text) for _, text in pairs]


def test_rerank_reorders_head_and_keeps_tail(monkeypatch, tmp_path):
    monkeypatch.setattr(rerank, "get_reranker", lambda: FakeModel())
    monkeypatch.setattr(rerank, "CACHE_DIR", tmp_path)

    chunks = [{"start": i * 10, "end": i * 10 + 10, "text": "x" * (i + 1)} for i in range(5)]
    r = rerank.make_rerank_ranker(lambda contract, clause: chunks, top_n=3)
    out = r({"title": "t"}, "Governing Law")

    assert [c["start"] for c in out] == [20, 10, 0, 30, 40]