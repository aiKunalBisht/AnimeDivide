"""
routers/pipeline.py
===================
Endpoint to execute the full narrative-analysis pipeline for a show.

Routes
------
POST /pipeline/run/{slug}  — run scrape → embed → analyse → store for a show
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks

router = APIRouter()


# ── POST /pipeline/run/{slug} ─────────────────────────────────────────────────
@router.post("/run/{slug}", summary="Run the full analysis pipeline for a show")
def run_pipeline(slug: str, background_tasks: BackgroundTasks) -> dict:
    """
    Execute the end-to-end pipeline for *slug*:

    1. Scrape episode/chapter data      (routers.scraper)
    2. Embed synopsis text              (sentence-transformers)
    3. Run narrative arc analysis       (Groq LLM)
    4. Persist results                  (SQLAlchemy → PostgreSQL)

    The pipeline is dispatched as a background task; the response returns
    immediately with a job token that the client can poll.

    TODO:
        - Validate that *slug* exists in the `shows` table.
        - Generate and persist a real job_id (UUID) in a `jobs` table.
        - Wire up each pipeline stage as a proper task chain
          (APScheduler or Celery).
    """
    if not slug:
        raise HTTPException(status_code=400, detail="slug must not be empty")

    def _run_pipeline(show_slug: str) -> None:
        """
        Stub pipeline — replace with real stage calls:
            scrape(show_slug)
            embed(show_slug)
            analyse(show_slug)
            store(show_slug)
        """
        pass

    background_tasks.add_task(_run_pipeline, slug)

    return {
        "slug": slug,
        "job_id": None,          # TODO: generate and return a real UUID
        "job_status": "queued",
        "stages": ["scrape", "embed", "analyse", "store"],
        "message": f"Pipeline queued for '{slug}'. Poll /pipeline/status/{{job_id}} for updates.",
        "_status": "stub — pipeline stages not yet implemented",
    }
