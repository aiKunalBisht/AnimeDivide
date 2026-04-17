"""
routers/scraper.py
==================
Endpoint to trigger on-demand scraping of MAL reviews for a show.

Routes
------
POST /scrape/{slug}  — scrape reviews for the given show, persist to raw_posts
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.models.database import Show, get_db
from backend.services.mal_scraper import scrape_reviews, save_reviews

router = APIRouter()
log = logging.getLogger(__name__)


# ── POST /scrape/{slug} ───────────────────────────────────────────────────────

@router.post("/{slug}", summary="Scrape MAL reviews for a show")
def scrape_show(slug: str, db: Session = Depends(get_db)) -> dict:
    """
    Look up the show by *slug*, scrape its MAL reviews, and persist
    new posts into the ``raw_posts`` table.

    Returns
    -------
    dict
        ``{"show": slug, "new_posts": <int>}``
    """
    if not slug:
        raise HTTPException(status_code=400, detail="slug must not be empty")

    # ── Look up show ──────────────────────────────────────────────────────
    show = db.query(Show).filter(Show.slug == slug).first()

    if show is None:
        raise HTTPException(
            status_code=404,
            detail=f"Show with slug '{slug}' not found in database.",
        )

    # ── Scrape ────────────────────────────────────────────────────────────
    log.info("Scraping reviews for '%s' (mal_id=%d)…", slug, show.mal_id)
    reviews = scrape_reviews(mal_id=show.mal_id, show_id=show.id)

    # ── Persist ───────────────────────────────────────────────────────────
    new_posts = save_reviews(reviews, db)

    return {
        "show": slug,
        "reviews_scraped": len(reviews),
        "new_posts": new_posts,
    }
