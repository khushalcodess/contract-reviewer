from src.reference_clauses import REFERENCE

KEYS = {"standard", "high_risk", "medium_risk", "low_risk", "safe_wording"}


def test_every_entry_is_complete():
    for name, entry in REFERENCE.items():
        assert set(entry) == KEYS, name
        for key in KEYS:
            assert entry[key], f"{name}: {key} is empty"