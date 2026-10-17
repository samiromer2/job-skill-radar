# Job Skill Radar

A small data service that reads job postings, extracts the skills they ask for, and ranks which skills show up most across the market.

**Business question:** *Which skills do employers actually ask for, and how often?* Instead of reading postings one by one, Job Skill Radar turns a pile of them into a ranked, queryable picture of demand.

Built with **FastAPI + PostgreSQL + SQLAlchemy**, fully containerized, and covered by tests.

## What it does

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/health` | GET | Liveness check |
| `/extract` | POST | Pull the skills out of a block of posting text (no save) |
| `/postings` | POST | Save a posting (title, company, text) and its extracted skills |
| `/skills/top` | GET | **The payoff:** rank skills by how many postings mention them, with each skill's share of all postings |

`/skills/top` is a straight SQL aggregation — a `GROUP BY` over the skills table with a percentage computed against the total number of postings:

```sql
SELECT skill,
       COUNT(*) AS postings,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM postings), 1) AS pct
FROM posting_skills
GROUP BY skill
ORDER BY postings DESC, skill
LIMIT :limit;
```

## How skills are detected

A configurable keyword/regex dictionary in [`app/skills.py`](app/skills.py) with word-boundary matching, so `"Java"` doesn't match inside `"JavaScript"`. It currently tracks **Python, SQL, Docker, AWS, CI/CD, and Kubernetes** — extend coverage by adding entries to the `SKILLS` map.

## Data model

Two tables keep the "top skills" query simple:

- **`postings`** — `id`, `title`, `company`, `text`, `created_at`
- **`posting_skills`** — one row per skill per posting (`posting_id`, `skill`), so counting demand is a plain aggregate

## Tech stack

Python · FastAPI · SQLAlchemy 2.0 (typed `Mapped` models) · PostgreSQL 16 · Docker Compose · pytest

## Run it

**With Docker (api + Postgres):**

```bash
docker compose up --build -d
docker compose logs -f api        # wait for "Application startup complete"
# open http://localhost:8000/docs
```

**Locally:**

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload     # open http://localhost:8000/docs
```

## Example

```bash
curl -X POST localhost:8000/postings \
  -H "Content-Type: application/json" \
  -d '{"title":"Data Analyst","company":"Acme","text":"Looking for Python, SQL and Docker experience."}'
# → {"id": 1, "skills": ["Docker", "Python", "SQL"]}

curl localhost:8000/skills/top
# → [{"skill": "Python", "postings": 1, "pct": 100.0}, ...]
```

## Tests

```bash
pytest -v        # unit tests for skill extraction + API tests
```

## Roadmap

Early but working. Planned next steps:

- Grow the skill taxonomy beyond the current six (aliases, categories, soft skills).
- Bulk-import postings from a CSV so a real dataset can be analyzed at once.
- A notebook / dashboard that charts top skills and how demand shifts over time.
- De-duplicate near-identical postings before counting.
