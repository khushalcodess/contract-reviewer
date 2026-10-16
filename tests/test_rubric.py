from src.reference_clauses import REFERENCE
from src.rubric import load_rubric


def test_every_clause_has_all_three_levels():
    rubric = load_rubric()
    for name in REFERENCE:
        assert name in rubric, f"{name} missing from the rubric"
        for level in ("Low", "Medium", "High"):
            assert rubric[name][level], f"{name}: {level} is empty"


def test_parsing_a_small_file(tmp_path):
    f = tmp_path / "r.md"
    f.write_text(
        "# T\n\n## A\n- Low: x\n- Medium: y\n- High: z\n- note here\n\n## Rules\n- r\n",
        encoding="utf-8",
    )
    assert load_rubric(f) == {
        "A": {"Low": "x", "Medium": "y", "High": "z", "notes": ["note here"]}
    }