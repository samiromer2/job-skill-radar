git clone https://github.com/samiromer2/job-skill-radar.git
cd job-skill-radar
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install fastapi "uvicorn[standard]" pytest httpx
pip freeze > requirements.txt


cd job-skill-radar
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pytest -v


