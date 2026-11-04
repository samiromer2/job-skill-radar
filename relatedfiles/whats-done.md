# What's Done

## Skill extractor
- `SKILLS` dict + `extract_skills()` regex matcher in `app/skills.py`
- Uses `(?<!\w)pattern(?!\w)` boundaries so `ci/cd` matches and `sql` does not match inside `postgresql`
- Unit tests in `tests/test_skills.py`

## API (FastAPI)
- `GET /health`
- `POST /extract` — text in, skills out (no DB)
- `POST /postings` — saves a posting (title, company, text) plus its extracted skills
- `GET /skills/top?limit=10` — hand-written aggregation SQL (count + % of postings)
- Endpoint tests in `tests/test_api.py` against a real Postgres

## Database
- Postgres 16 via Docker Compose (host port 5433)
- SQLAlchemy 2.x + psycopg 3; models `Posting` and `PostingSkill`
- Tables created at startup in the app lifespan (no Alembic yet)

## Docker
- `Dockerfile` + `.dockerignore` for the API
- `docker-compose.yml` runs `db` + `api` (API at http://localhost:8000/docs)

## CI/CD
- GitHub Actions: `test` job (Postgres service, ruff, pytest) then `build` job (compose up + `/health` smoke test)
- `main` is protected by the `test` and `build` checks

## Docs
- README with project details and usage
- `CLAUDE.md` with project context
