import pytest
from pydantic import ValidationError

from src.schema import ClauseFinding

FULL = dict(risk_level="High", explanation="e", cited_text="c", suggested_redline="r")


def test_found_requires_all_fields():
    with pytest.raises(ValidationError):
        ClauseFinding(clause="Governing Law", found=True, risk_level="Low")


def test_not_found_must_be_empty():
    with pytest.raises(ValidationError):
        ClauseFinding(clause="Governing Law", found=False, explanation="x")


def test_valid_findings():
    ClauseFinding(clause="Governing Law", found=False)
    ClauseFinding(clause="Governing Law", found=True, **FULL)


def test_bad_risk_level_rejected():
    with pytest.raises(ValidationError):
        ClauseFinding(clause="x", found=True, **{**FULL, "risk_level": "Severe"})