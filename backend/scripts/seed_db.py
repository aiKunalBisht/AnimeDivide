"""
seed_db.py
==========
Inserts seed shows into the `shows` table.

Usage
-----
    python backend/scripts/seed_db.py                      # uses DATABASE_URL from env
    DATABASE_URL=sqlite:///./dev.db python backend/scripts/seed_db.py

Supported databases
-------------------
    SQLite   : sqlite:///./dev.db
    PostgreSQL: postgresql://user:pass@localhost:5432/mydb
    MySQL    : mysql+pymysql://user:pass@localhost:3306/mydb

Requirements
------------
    pip install sqlalchemy
    pip install psycopg2-binary   # only if using PostgreSQL
    pip install pymysql           # only if using MySQL

Table schema expected (auto-created if it doesn't exist)
---------------------------------------------------------
    CREATE TABLE shows (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        slug      TEXT UNIQUE NOT NULL,
        title_en  TEXT NOT NULL,
        title_jp  TEXT NOT NULL,
        mal_id    INTEGER UNIQUE NOT NULL,
        genres    TEXT NOT NULL,          -- JSON-encoded list
        year      INTEGER NOT NULL
    );
"""

import json
import os
import sys
from pathlib import Path

# ── Resolve project root so the script works from any working directory ────────
ROOT = Path(__file__).resolve().parents[2]          # backend/scripts/ → project root
sys.path.insert(0, str(ROOT))

from backend.data.shows_seed import SHOWS           # noqa: E402  (after sys.path fix)

# ── Database setup ─────────────────────────────────────────────────────────────
try:
    from sqlalchemy import (
        Column, Integer, String, Text,
        UniqueConstraint, create_engine, text,
    )
    from sqlalchemy.orm import DeclarativeBase, Session
except ImportError:
    sys.exit(
        "SQLAlchemy is not installed.\n"
        "Run: pip install sqlalchemy\n"
        "     pip install psycopg2-binary   # for PostgreSQL\n"
        "     pip install pymysql           # for MySQL"
    )

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

engine = create_engine(DATABASE_URL, echo=False)


# ── ORM model ─────────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


class Show(Base):
    __tablename__ = "shows"
    __table_args__ = (UniqueConstraint("slug", name="uq_shows_slug"),)

    id       = Column(Integer, primary_key=True, autoincrement=True)
    slug     = Column(String(128), nullable=False, unique=True)
    title_en = Column(String(256), nullable=False)
    title_jp = Column(String(256), nullable=False)
    mal_id   = Column(Integer,     nullable=False, unique=True)
    genres   = Column(Text,        nullable=False)   # stored as JSON string
    year     = Column(Integer,     nullable=False)

    def __repr__(self) -> str:
        return f"<Show slug={self.slug!r} year={self.year}>"


# ── Helpers ────────────────────────────────────────────────────────────────────
def _row_exists(session: Session, slug: str) -> bool:
    """Return True if a row with this slug already exists."""
    result = session.execute(
        text("SELECT 1 FROM shows WHERE slug = :slug LIMIT 1"),
        {"slug": slug},
    )
    return result.fetchone() is not None


# ── Main seeding routine ───────────────────────────────────────────────────────
def seed() -> None:
    print(f"[seed_db] Connecting to: {DATABASE_URL}")

    # Create table if it doesn't exist yet
    Base.metadata.create_all(engine)
    print("[seed_db] Table `shows` ready.")

    inserted = 0
    skipped  = 0

    with Session(engine) as session:
        for record in SHOWS:
            if _row_exists(session, record["slug"]):
                print(f"  [SKIP]   {record['slug']} — already in DB")
                skipped += 1
                continue

            show = Show(
                slug     = record["slug"],
                title_en = record["title_en"],
                title_jp = record["title_jp"],
                mal_id   = record["mal_id"],
                genres   = json.dumps(record["genres"], ensure_ascii=False),
                year     = record["year"],
            )
            session.add(show)

            try:
                session.flush()   # write to DB while still in the transaction
                print(f"  [INSERT] {record['slug']} ({record['year']})")
                inserted += 1
            except Exception as exc:
                session.rollback()
                print(f"  [ERROR]  {record['slug']} — {exc}")
                skipped += 1

        session.commit()

    print(
        f"\n[seed_db] Done. "
        f"{inserted} inserted / {skipped} skipped / {len(SHOWS)} total."
    )


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    seed()
