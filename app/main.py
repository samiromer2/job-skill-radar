import hashlib
from contextlib import asynccontextmanager
from datetime import date
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db
from app.models import Posting, PostingSkill
from app.skills import extract_skills


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)  # creates tables if missing
    yield


app = FastAPI(title="Job Skill Radar", lifespan=lifespan)
DbSession = Annotated[Session, Depends(get_db)]


class ExtractIn(BaseModel):
    text: str


class PostingIn(BaseModel):
    title: str = Field(max_length=200)
    company: str | None = Field(default=None, max_length=200)
    text: str = Field(min_length=1)
    posted_date: date | None = None
    source_url: str | None = Field(default=None, max_length=500)


def text_hash(posting_text: str) -> str:
    """Fingerprint ignoring case and whitespace, so re-imports don't double count."""
    normalized = " ".join(posting_text.lower().split())
    return hashlib.sha256(normalized.encode()).hexdigest()


def new_posting(body: PostingIn, digest: str) -> Posting:
    return Posting(
        title=body.title,
        company=body.company,
        text=body.text,
        text_hash=digest,
        posted_date=body.posted_date,
        source_url=body.source_url,
        skills=[PostingSkill(skill=s) for s in extract_skills(body.text)],
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/extract")
def extract(body: ExtractIn):
    return {"skills": sorted(extract_skills(body.text))}


@app.post("/postings", status_code=201)
def create_posting(body: PostingIn, db: DbSession):
    digest = text_hash(body.text)
    if db.scalar(select(Posting.id).where(Posting.text_hash == digest)):
        raise HTTPException(409, "A posting with the same text already exists")
    posting = new_posting(body, digest)
    db.add(posting)
    db.commit()
    return {"id": posting.id, "skills": sorted(s.skill for s in posting.skills)}


@app.post("/postings/import")
def import_postings(
    postings: Annotated[list[PostingIn], Field(min_length=1, max_length=1000)],
    db: DbSession,
):
    digests = {text_hash(p.text): p for p in postings}  # later copy in a batch wins
    existing = set(
        db.scalars(select(Posting.text_hash).where(Posting.text_hash.in_(digests)))
    )
    new = [new_posting(p, d) for d, p in digests.items() if d not in existing]
    db.add_all(new)
    db.commit()
    return {
        "received": len(postings),
        "imported": len(new),
        "skipped_duplicates": len(postings) - len(new),
    }


@app.get("/skills/top")
def top_skills(db: DbSession, limit: int = 10):
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
