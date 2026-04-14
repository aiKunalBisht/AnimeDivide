"""
routers/scraper.py
==================
Endpoint to trigger on-demand scraping of episode/chapter data for a show.

Routes
------
POST /scrape/{slug}  — kick off a scrape job for the given show
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks

router = APIRouter()


# ── POST /scrape/{slug} ───────────────────────────────────────────────────────
@router.post("/{slug}", summary="Scrape episode data for a show")
def scrape_show(slug: str, background_tasks: BackgroundTasks) -> dict:
    """
    Trigger a scrape job that fetches episode/chapter metadata for *slug*
    from MyAnimeList (and any configured secondary sources).

    The job is dispatched to a background worker so the request returns
    immediately with a job token.

    TODO:
        - Validate that *slug* exists in the `shows` table.
        - Enqueue a Celery / APScheduler task instead of a background thread.
        - Persist fetched episodes into the `episodes` table.
    """
    if not slug:
        raise HTTPException(status_code=400, detail="slug must not be empty")

    # Placeholder background task (no-op until scraper service is implemented)
    def _scrape_job(show_slug: str) -> None:
        """Stub — replace with real MAL / scraper call."""
        pass

    background_tasks.add_task(_scrape_job, slug)

    return {
        "slug": slug,
        "job_status": "queued",
        "message": f"Scrape job queued for '{slug}'.",
        "_status": "stub — scraper service not yet implemented",
    }
