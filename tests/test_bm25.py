from src.bm25 import tokenize


def test_tokenize_drops_stopwords_and_lowercases():
    assert tokenize("The Agreement IS governed by Illinois law") == [
        "agreement", "governed", "illinois", "law",
    ]


def test_tokenize_keeps_negations():
    assert "not" in tokenize("shall not compete")