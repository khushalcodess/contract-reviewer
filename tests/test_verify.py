from src.verify import find_citation

SRC = "6.9 Governing Law. This Agreement is to be construed according to the laws          of the State of Illinois.\n7. NEW"


def test_finds_despite_whitespace_and_case():
    span = find_citation("Construed according to the laws of the State of Illinois", SRC)
    assert span is not None
    s, e = span
    assert SRC[s:e].startswith("construed") and SRC[s:e].endswith("Illinois")


def test_returns_none_for_text_not_in_source():
    assert find_citation("governed by the laws of France", SRC) is None


def test_empty_citation_is_not_verified():
    assert find_citation("   ", SRC) is None


def test_offset_shifts_positions():
    s, e = find_citation("NEW", SRC, offset=1000)
    assert SRC[s - 1000 : e - 1000] == "NEW"