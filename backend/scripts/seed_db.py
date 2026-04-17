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
    SQLite    : sqlite:///./dev.db
    PostgreSQL: postgresql://user:pass@localhost:5432/mydb
    MySQL     : mysql+pymysql://user:pass@localhost:3306/mydb
"""

import json
import sys
from pathlib import Path

from sqlalchemy import text

# ── Resolve project root so the script works from any working directory ────────
ROOT = Path(__file__).resolve().parents[2]   # backend/scripts/ → project root
sys.path.insert(0, str(ROOT))

from backend.data.shows_seed import SHOWS                    # noqa: E402
from backend.models.database import Show, engine, init_db   # noqa: E402
from sqlalchemy.orm import Session                           # noqa: E402


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
    from backend.models.database import DATABASE_URL
    print(f"[seed_db] Connecting to: {DATABASE_URL}")

    # Create all tables (idempotent)
    init_db()
    print("[seed_db] Tables ready.")

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
