from fastapi import FastAPI
from pydantic import BaseModel
from app.skills import extract_skills

app = FastAPI(title="Job Skill Radar")

class Posting(BaseModel):
    text: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/extract")
def extract(posting: Posting):
    return {"skills": sorted(extract_skills(posting.text))}