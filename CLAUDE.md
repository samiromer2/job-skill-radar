# Job Skill Radar

FastAPI service that extracts skills from job postings, stores them in Postgres,
and returns stats: top skills, trends over time, and a gap score against the
user's own skill list. Portfolio project telling two stories: analyst (data
cleaning, text parsing, aggregation SQL) and backend engineering (Docker, CI/CD,
cloud). Python only, no PHP.

Repo: https://github.com/samiromer2/job-skill-radar

## Stack

- Python 3.12 (CI and Docker image), FastAPI, Pydantic, SQLAlchemy 2.x, psycopg 3
- Postgres 16 in Docker Compose
- pytest + httpx (TestClient), ruff (lint + format)
- GitHub Actions CI

## Layout

```
app/
  main.py      API endpoints, lifespan creates tables (no Alembic yet)
  db.py        engine, SessionLocal, Base, get_db; DATABASE_URL env var
  models.py    Posting, PostingSkill (one row per skill per posting)
  skills.py    SKILLS dict + extract_skills() regex matcher
tests/
  test_skills.py   extractor unit tests
  test_api.py      endpoint tests against a real Postgres
.github/workflows/ci.yml   test job (Postgres service, ruff, pytest) -> build job (compose up + /health smoke test)
Dockerfile, .dockerignore, docker-compose.yml (db + api)
requirements.txt (runtime), requirements-dev.txt (pytest, httpx, ruff)
```

## Endpoints

- `GET /health`
- `POST /extract` — text in, skills out (no DB)
- `POST /postings` — save posting (title, company, text) + extracted skills
- `GET /skills/top?limit=10` — hand-written aggregation SQL (count + pct of postings)

## Commands

```bash
conda deactivate && source .venv/bin/activate   # always use .venv, not Conda base
docker compose up -d --build                    # db + api; API at http://localhost:8000/docs
docker compose logs -f api
python -m pytest -v                             # needs the db container running
ruff format . && ruff check .                   # run before every commit
```

## Conventions

- DB dependency: `DbSession = Annotated[Session, Depends(get_db)]` (ruff B008 rejects `Depends()` as a default)
- Analytics queries are written as raw SQL via `sqlalchemy.text()` on purpose — it is the analyst showcase
- Skill matching uses `(?<!\w)pattern(?!\w)` boundaries, not `\b`, so `ci/cd` works and `sql` does not match `postgresql`
- Work on a branch, open a PR; `main` is protected by the `test` and `build` checks
- Keep `requirements.txt` hand-written and minimal (never `pip freeze` from Conda)

## Gotchas

- Local Postgres is on host port **5433** (another Postgres on the Mac owns 5432). Inside Compose the API uses `db:5432`.
- Docker Desktop must be running. Start containers only with `docker compose`, never Docker Desktop's Run button (it created a stray container that broke Compose once).
- Tests currently write into the dev database; a separate test DB is a planned improvement.

## Status and next steps

Done: extractor, API, Postgres, Dockerized API, CI pipeline.

Next, in order:
1. Bulk import endpoint `POST /postings/import` for the user's ~262 real postings. Ask the user what format they are in before designing it.
2. Expand `SKILLS` dict based on what real postings miss.
3. Trends over time endpoint.
4. User skill list + gap score endpoint.
5. Separate test database; Alembic migrations.
6. AWS deploy, JWT auth, security scanning, README with architecture diagram.
