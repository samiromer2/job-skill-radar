from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

class Posting(Base):
    __tablename__ = "postings"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    company: Mapped[str | None] = mapped_column(String(200))
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    skills: Mapped[list["PostingSkill"]] = relationship(cascade="all, delete-orphan")

class PostingSkill(Base):
    __tablename__ = "posting_skills"
    posting_id: Mapped[int] = mapped_column(ForeignKey("postings.id"), primary_key=True)
    skill: Mapped[str] = mapped_column(String(50), primary_key=True)