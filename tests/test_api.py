from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_unsupported_file_type_is_rejected_before_any_work():
    r = client.post("/contracts", files={"file": ("x.exe", b"abc")})
    assert r.status_code == 400