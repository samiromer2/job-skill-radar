from datetime import UTC, date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Posting(Base):
    __tablename__ = "postings"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    company: Mapped[str | None] = mapped_column(String(200))
    text: Mapped[str] = mapped_column(Text)
    # sha256 of the normalized text, so the same posting is only counted once
    text_hash: Mapped[str] = mapped_column(String(64), unique=True)
    posted_date: Mapped[date | None] = mapped_column(Date)
    source_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    skills: Mapped[list["PostingSkill"]] = relationship(cascade="all, delete-orphan")


class PostingSkill(Base):
    __tablename__ = "posting_skills"
    posting_id: Mapped[int] = mapped_column(ForeignKey("postings.id"), primary_key=True)
    skill: Mapped[str] = mapped_column(String(50), primary_key=True)
