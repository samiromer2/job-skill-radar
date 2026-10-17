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




docker compose up --build -d
docker compose ps                 # both db and api should be running
docker compose logs api           # look for "Application startup complete"


docker compose up --build -d      # rebuild after code changes
docker compose logs -f api        # follow the logs
docker compose down               # stop everything (data is kept)

docker ps -a                              # you'll see the odd one, bc2bf6786167
docker rm -f bc2bf6786167                 # delete that stray container
docker compose down --remove-orphans      # clean up the project
docker compose up -d
docker compose ps                         # db and api should both show "running"


conda deactivate
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -v


