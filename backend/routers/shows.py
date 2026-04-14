"""
routers/shows.py
================
Endpoints for retrieving anime show data and narrative summaries.

Routes
------
GET /shows                  — paginated list of all shows
GET /shows/{slug}           — single show metadata
GET /shows/{slug}/narrative — generated narrative arc for a show
"""

from fastapi import APIRouter, HTTPException, Query

router = APIRouter()


# ── GET /shows ────────────────────────────────────────────────────────────────
@router.get("", summary="List all shows")
def list_shows(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    per_page: int = Query(20, ge=1, le=100, description="Results per page"),
) -> dict:
    """
    Return a paginated list of all seeded anime shows.

    TODO: query the `shows` table via SQLAlchemy and return real rows.
    """
    return {
        "page": page,
        "per_page": per_page,
        "total": 0,
        "shows": [],
        "_status": "stub — database query not yet implemented",
    }


# ── GET /shows/{slug} ─────────────────────────────────────────────────────────
@router.get("/{slug}", summary="Get a single show by slug")
def get_show(slug: str) -> dict:
    """
    Return metadata for a single show identified by its URL-safe slug.

    TODO: fetch from `shows` table; raise 404 if not found.
    """
    # Placeholder — replace with real DB lookup
    if not slug:
        raise HTTPException(status_code=400, detail="slug must not be empty")

    return {
        "slug": slug,
        "title_en": None,
        "title_jp": None,
        "mal_id": None,
        "genres": [],
        "year": None,
        "_status": "stub — database query not yet implemented",
    }


# ── GET /shows/{slug}/narrative ───────────────────────────────────────────────
@router.get("/{slug}/narrative", summary="Get narrative arc for a show")
def get_narrative(slug: str) -> dict:
    """
    Return the generated narrative arc analysis for a show.

    TODO: fetch pre-computed narrative from the `narratives` table,
          or trigger the pipeline and return a job ID if not ready.
    """
    return {
        "slug": slug,
        "arcs": [],
        "themes": [],
        "sentiment_trajectory": [],
        "_status": "stub — pipeline not yet wired",
    }
