git clone https://github.com/samiromer2/job-skill-radar.git
cd job-skill-radar
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install fastapi "uvicorn[standard]" pytest httpx
pip freeze > requirements.txt


cd job-skill-radar
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pytest -v


pytest                              # both tests should pass
uvicorn app.main:app --reload       # then open http://localhost:8000/docs

docker compose up -d      # starts Postgres in the background
docker compose ps         # should show "db" as running

docker compose exec db psql -U app -d skillradar -c "SELECT * FROM posting_skills;"

git add .
git commit -m "Add Postgres, save postings, top skills endpoint"
git push

