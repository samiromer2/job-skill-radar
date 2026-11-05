import uuid

from fastapi.testclient import TestClient

from app.main import app


def unique(text: str) -> str:
    # Tests share the dev database, and identical text is rejected as a duplicate
    return f"{text} {uuid.uuid4()}"


def test_health():
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}


def test_create_posting_and_top_skills():
    with TestClient(app) as client:
        r = client.post(
            "/postings", json={"title": "Dev", "text": unique("Python and Docker")}
        )
        assert r.status_code == 201
        assert r.json()["skills"] == ["Docker", "Python"]
        top = client.get("/skills/top").json()
        assert "Python" in [row["skill"] for row in top]


def test_duplicate_posting_is_rejected():
    with TestClient(app) as client:
        body = {"title": "Dev", "text": unique("SQL")}
        assert client.post("/postings", json=body).status_code == 201
        body["text"] = "  " + body["text"].upper() + "  "  # same text, other case
        assert client.post("/postings", json=body).status_code == 409


def test_import_skips_duplicates():
    a, b = unique("Python, AWS"), unique("Kubernetes")
    batch = [
        {"title": "A", "text": a, "posted_date": "2026-09-01"},
        {"title": "B", "company": "Acme", "text": b},
        {"title": "A again", "text": a},
    ]
    with TestClient(app) as client:
        first = client.post("/postings/import", json=batch).json()
        assert first == {"received": 3, "imported": 2, "skipped_duplicates": 1}
        again = client.post("/postings/import", json=batch).json()
        assert again == {"received": 3, "imported": 0, "skipped_duplicates": 3}


def test_import_rejects_bad_input():
    with TestClient(app) as client:
        assert client.post("/postings/import", json=[]).status_code == 422
        bad_date = [{"title": "A", "text": "x", "posted_date": "Sept"}]
        assert client.post("/postings/import", json=bad_date).status_code == 422
