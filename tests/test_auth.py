import pytest

from src import auth


@pytest.fixture(autouse=True)
def secret(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "x" * 40)


def test_password_hash_roundtrip():
    h = auth.hash_password("correct horse")
    assert h != "correct horse"
    assert auth.verify_password("correct horse", h)
    assert not auth.verify_password("wrong", h)


def test_token_roundtrip():
    assert auth.read_token(auth.make_token(7)) == 7


def test_tampered_token_rejected():
    t = auth.make_token(7)
    flipped = "A" if t[-5] != "A" else "B"
    assert auth.read_token(t[:-5] + flipped + t[-4:]) is None


def test_expired_token_rejected():
    assert auth.read_token(auth.make_token(7, now=1000)) is None


def test_missing_secret_raises(monkeypatch):
    monkeypatch.delenv("JWT_SECRET")
    with pytest.raises(RuntimeError):
        auth.make_token(1)