from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db
from app.models import Posting, PostingSkill
from app.skills import extract_skills


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)  # creates tables if missing
    yield


app = FastAPI(title="Job Skill Radar", lifespan=lifespan)


class ExtractIn(BaseModel):
    text: str


class PostingIn(BaseModel):
    title: str
    company: str | None = None
    text: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/extract")
def extract(body: ExtractIn):
    return {"skills": sorted(extract_skills(body.text))}


@app.post("/postings", status_code=201)
def create_posting(body: PostingIn, db: Session = Depends(get_db)):
    skills = sorted(extract_skills(body.text))
    posting = Posting(
        title=body.title,
        company=body.company,
        text=body.text,
        skills=[PostingSkill(skill=s) for s in skills],
    )
    db.add(posting)
    db.commit()
    return {"id": posting.id, "skills": skills}


@app.get("/skills/top")
def top_skills(limit: int = 10, db: Session = Depends(get_db)):
    rows = (
        db.execute(
            text("""
        SELECT skill,
               COUNT(*) AS postings,
               ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM postings), 1) AS pct
        FROM posting_skills
        GROUP BY skill
        ORDER BY postings DESC, skill
        LIMIT :limit
    """),
            {"limit": limit},
        )
        .mappings()
        .all()
    )
    return [dict(r) for r in rows]
