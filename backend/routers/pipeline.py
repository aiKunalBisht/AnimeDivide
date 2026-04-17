"""
routers/pipeline.py
===================
Endpoint to execute the full narrative-analysis pipeline for a show.

Routes
------
POST /pipeline/run/{slug}  — run scrape → embed → analyse → store for a show
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.models.database import Show, get_db
from backend.services.nlp_pipeline import run_pipeline as run_nlp_pipeline

router = APIRouter()
log = logging.getLogger(__name__)

# ── POST /pipeline/run/{slug} ─────────────────────────────────────────────────
@router.post("/run/{slug}", summary="Run the full analysis pipeline for a show")
def run_pipeline_endpoint(slug: str, db: Session = Depends(get_db)) -> dict:
    """
    Execute the end-to-end pipeline for *slug* synchronously:
    
    1. Fetch unanalysed posts
    2. Detect topic and score sentiment (Groq LLM)
    3. Persist results iteratively
    4. Compute and upsert divide scores
    """
    if not slug:
        raise HTTPException(status_code=400, detail="slug must not be empty")

    show = db.query(Show).filter(Show.slug == slug).first()
    
    if not show:
        raise HTTPException(
            status_code=404, 
            detail=f"Show with slug '{slug}' not found in database."
        )
        
    log.info("Starting pipeline for show '%s' (id=%d)", slug, show.id)
    summary = run_nlp_pipeline(show.id, db)
    
    return summary
