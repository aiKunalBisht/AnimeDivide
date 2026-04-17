"""
database.py
===========
SQLAlchemy ORM models for the anime-divide project.

Tables
------
    shows              – one row per anime title
    raw_posts          – scraped reviews / comments
    sentiment_results  – per-topic sentiment scores for each post
    divide_scores      – aggregated JP-vs-EN divide metric per show/topic

Session dependency
------------------
    get_db()  – FastAPI Depends() helper that yields a scoped Session

Configuration
-------------
    DATABASE_URL env var (default: sqlite:///./dev.db)
"""

import os
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, relationship

# ── Engine ─────────────────────────────────────────────────────────────────────

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

# `check_same_thread=False` is only relevant for SQLite but harmless elsewhere.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False,
)


# ── Declarative base ───────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    pass


# ── Helpers ────────────────────────────────────────────────────────────────────

def _now() -> datetime:
    """Return the current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


# ── 1. shows ──────────────────────────────────────────────────────────────────

class Show(Base):
    """One row per anime title."""

    __tablename__ = "shows"
    __table_args__ = (
        UniqueConstraint("slug",   name="uq_shows_slug"),
        UniqueConstraint("mal_id", name="uq_shows_mal_id"),
        Index("ix_shows_slug", "slug"),
    )

    id         = Column(Integer, primary_key=True, autoincrement=True)
    slug       = Column(String(128), nullable=False, unique=True, index=True)
    title_en   = Column(String(256), nullable=False)
    title_jp   = Column(String(256), nullable=False)
    mal_id     = Column(Integer,     nullable=False, unique=True)
    genres     = Column(Text,        nullable=False)   # JSON-encoded list, e.g. '["Action","Drama"]'
    year       = Column(Integer,     nullable=False)
    narrative  = Column(Text,        nullable=True)
    created_at = Column(DateTime,    nullable=False, default=_now)

    # relationships
    raw_posts       = relationship("RawPost",       back_populates="show", cascade="all, delete-orphan")
    sentiment_results = relationship("SentimentResult", back_populates="show", cascade="all, delete-orphan")
    divide_scores   = relationship("DivideScore",   back_populates="show", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Show slug={self.slug!r} year={self.year}>"


# ── 2. raw_posts ───────────────────────────────────────────────────────────────

class RawPost(Base):
    """Scraped review or comment from MAL (English or Japanese)."""

    __tablename__ = "raw_posts"
    __table_args__ = (
        UniqueConstraint("post_hash", name="uq_raw_posts_hash"),
    )

    id         = Column(Integer, primary_key=True, autoincrement=True)
    show_id    = Column(Integer, ForeignKey("shows.id", ondelete="CASCADE"), nullable=False, index=True)
    source     = Column(String(16),  nullable=False)   # "mal_en" | "mal_jp"
    language   = Column(String(8),   nullable=False)   # "en" | "jp"
    username   = Column(String(128), nullable=False)
    text       = Column(Text,        nullable=False)
    score      = Column(Integer,     nullable=True)    # 1-10, may be absent
    scraped_at = Column(DateTime,    nullable=False, default=_now)
    post_hash  = Column(String(32),  nullable=False, unique=True)  # MD5 of text

    # relationships
    show              = relationship("Show",            back_populates="raw_posts")
    sentiment_results = relationship("SentimentResult", back_populates="raw_post", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<RawPost id={self.id} show_id={self.show_id} lang={self.language!r}>"


# ── 3. sentiment_results ───────────────────────────────────────────────────────

class SentimentResult(Base):
    """Per-topic sentiment score derived from a single raw post."""

    __tablename__ = "sentiment_results"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    raw_post_id     = Column(Integer, ForeignKey("raw_posts.id", ondelete="CASCADE"), nullable=False, index=True)
    show_id         = Column(Integer, ForeignKey("shows.id",     ondelete="CASCADE"), nullable=False, index=True)
    language        = Column(String(8),  nullable=False)   # "en" | "jp"
    topic           = Column(String(32), nullable=False)   # ost | animation | story | characters | faithfulness | overall
    sentiment_score = Column(Float,      nullable=False)   # –1.0 … +1.0
    processed_at    = Column(DateTime,   nullable=False, default=_now)

    # relationships
    raw_post = relationship("RawPost", back_populates="sentiment_results")
    show     = relationship("Show",    back_populates="sentiment_results")

    def __repr__(self) -> str:
        return (
            f"<SentimentResult post={self.raw_post_id} topic={self.topic!r} "
            f"score={self.sentiment_score:.3f}>"
        )


# ── 4. divide_scores ──────────────────────────────────────────────────────────

class DivideScore(Base):
    """
    Aggregated JP-vs-EN sentiment divide for a show / topic pair.
    divide_score = jp_avg_score – en_avg_score
    """

    __tablename__ = "divide_scores"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    show_id        = Column(Integer, ForeignKey("shows.id", ondelete="CASCADE"), nullable=False, index=True)
    topic          = Column(String(32), nullable=False)
    jp_avg_score   = Column(Float,   nullable=False)
    en_avg_score   = Column(Float,   nullable=False)
    divide_score   = Column(Float,   nullable=False)   # jp_avg_score – en_avg_score
    post_count_jp  = Column(Integer, nullable=False)
    post_count_en  = Column(Integer, nullable=False)
    computed_at    = Column(DateTime, nullable=False, default=_now)

    # relationship
    show = relationship("Show", back_populates="divide_scores")

    def __repr__(self) -> str:
        return (
            f"<DivideScore show={self.show_id} topic={self.topic!r} "
            f"divide={self.divide_score:.3f}>"
        )


# ── FastAPI session dependency ─────────────────────────────────────────────────

def get_db():
    """
    Yield a SQLAlchemy Session for use with FastAPI's Depends().

    Usage
    -----
        from backend.models.database import get_db

        @router.get("/shows")
        def list_shows(db: Session = Depends(get_db)):
            return db.query(Show).all()
    """
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


# ── Convenience: create all tables ────────────────────────────────────────────

def init_db() -> None:
    """Create all tables in the database (idempotent)."""
    Base.metadata.create_all(engine)
