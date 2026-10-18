import pytest
from fastapi.testclient import TestClient

from app.main import app, current_user

client = TestClient(app)


@pytest.fixture
def as_user():
    app.dependency_overrides[current_user] = lambda: 1
    yield
    app.dependency_overrides.clear()


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_upload_requires_login():
    r = client.post("/contracts", files={"file": ("x.txt", b"abc")})
    assert r.status_code == 401


def test_list_requires_login():
    assert client.get("/contracts").status_code == 401


def test_bad_token_rejected(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "x" * 40)
    r = client.get("/contracts", headers={"Authorization": "Bearer nonsense"})
    assert r.status_code == 401


def test_unsupported_file_type_is_rejected(as_user):
    r = client.post("/contracts", files={"file": ("x.exe", b"abc")})
    assert r.status_code == 400


def test_other_users_contract_is_hidden(as_user, monkeypatch):
    from src import app_db
    monkeypatch.setattr(app_db, "contract_owner", lambda cid: 2)
    assert client.get("/contracts/5/findings").status_code == 404
    assert client.get("/contracts/5/text").status_code == 404
    assert client.delete("/contracts/5").status_code == 404


def test_missing_contract_returns_404(as_user, monkeypatch):
    from src import app_db
    monkeypatch.setattr(app_db, "contract_owner", lambda cid: None)
    assert client.delete("/contracts/999").status_code == 404


def test_retrieval_summary_averages_clauses(tmp_path, monkeypatch):
    import app.main as m
    (tmp_path / "results_bm25_test.csv").write_text(
        ",hit@1,hit@3,mrr\nA,1.0,1.0,1.0\nB,0.0,0.5,0.25\n", encoding="utf-8")
    monkeypatch.setattr(m, "EVAL_DIR", tmp_path)
    out = m._retrieval("test")
    assert out == [{"system": "bm25", "clauses": 1 + 1, "hit@1": 0.5, "hit@3": 0.75, "mrr": 0.625}]


def test_signup_rejects_short_password():
    r = client.post("/auth/signup", json={"email": "a@b.com", "password": "short"})
    assert r.status_code == 400


def test_signup_rejects_bad_email():
    r = client.post("/auth/signup", json={"email": "nope", "password": "longenough1"})
    assert r.status_code == 400


def test_login_wrong_password(monkeypatch):
    from src import app_db, auth
    monkeypatch.setenv("JWT_SECRET", "x" * 40)
    monkeypatch.setattr(app_db, "get_user_by_email",
                        lambda e: (1, auth.hash_password("rightpassword")))
    r = client.post("/auth/login", json={"email": "a@b.com", "password": "wrongpassword"})
    assert r.status_code == 401