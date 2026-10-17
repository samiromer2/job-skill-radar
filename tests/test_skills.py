from app.skills import extract_skills


def test_finds_skills():
    text = "Senior Python dev. Docker, AWS Lambda, GitHub Actions."
    assert extract_skills(text) == {"Python", "Docker", "AWS", "CI/CD"}


def test_no_partial_match():
    assert "SQL" not in extract_skills("We use PostgreSQL")
