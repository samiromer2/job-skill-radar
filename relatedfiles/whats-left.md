# What's Left

In order:

1. **Bulk import endpoint** — `POST /postings/import` for the ~262 real postings.
   - Open question: what format are the postings in (CSV, JSON, text files, ...)? Decide before designing.
2. **Expand the `SKILLS` dict** — based on what the real postings miss after import.
3. **Trends over time endpoint** — skill counts by period (raw SQL via `sqlalchemy.text()`).
4. **User skill list + gap score endpoint** — store the user's skills and score them against demand.
5. **Separate test database + Alembic migrations** — tests currently write into the dev DB.
6. **Production polish**
   - AWS deploy
   - JWT auth
   - Security scanning in CI
   - README with an architecture diagram
