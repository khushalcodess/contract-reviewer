from src.chunking import clause_chunks

SAMPLE = (
    "1. Term. This agreement lasts one year.\n\n"
    "2. Governing Law. This agreement is governed by the laws of Illinois.\n\n"
    "3. Notices. All notices must be in writing.\n\n"
    "4. Assignment. Neither party may assign this agreement.\n\n"
    "5. Fees. The customer shall pay all fees on time.\n\n"
    "6. Entire Agreement. This is the whole agreement.\n"
)


def test_positions_match_text():
    for ch in clause_chunks(SAMPLE, min_size=10, max_size=60, overlap=10):
        assert SAMPLE[ch["start"]:ch["end"]] == ch["text"]


def test_no_chunk_exceeds_max_size():
    for ch in clause_chunks(SAMPLE, min_size=10, max_size=60, overlap=10):
        assert ch["end"] - ch["start"] <= 60


def test_every_character_is_covered():
    covered = set()
    for ch in clause_chunks(SAMPLE, min_size=10, max_size=60, overlap=10):
        covered.update(range(ch["start"], ch["end"]))
    assert covered == set(range(len(SAMPLE)))


def test_splits_at_headings():
    chunks = clause_chunks(SAMPLE, min_size=10, max_size=1000)
    assert any(ch["text"].lstrip().startswith("2. Governing Law") for ch in chunks)