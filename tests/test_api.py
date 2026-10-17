from fastapi.testclient import TestClient

from app.main import app


def test_health():
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}


def test_create_posting_and_top_skills():
    with TestClient(app) as client:
        r = client.post("/postings", json={"title": "Dev", "text": "Python and Docker"})
        assert r.status_code == 201
        assert r.json()["skills"] == ["Docker", "Python"]
        top = client.get("/skills/top").json()
        assert "Python" in [row["skill"] for row in top]
