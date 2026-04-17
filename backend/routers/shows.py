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

import os
import json
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from groq import Groq
from dotenv import load_dotenv

from backend.models.database import Show, DivideScore, RawPost, get_db

load_dotenv()

router = APIRouter()

# ── GET /shows ────────────────────────────────────────────────────────────────
@router.get("", summary="List all shows")
def list_shows(db: Session = Depends(get_db)) -> list[dict]:
    """
    Return a list of all seeded anime shows, ordered by highest absolute
    divide score descending.
    """
    shows_db = db.query(Show).all()
    results = []
    
    for show in shows_db:
        divide_scores = db.query(DivideScore).filter(DivideScore.show_id == show.id).all()
        top_divide_obj = None
        
        if divide_scores:
            top_score = max(divide_scores, key=lambda d: abs(d.divide_score))
            top_divide_obj = {
                "topic": top_score.topic,
                "jp_score": top_score.jp_avg_score,
                "en_score": top_score.en_avg_score,
                "divide": top_score.divide_score
            }
            
        results.append({
            "slug": show.slug,
            "title_en": show.title_en,
            "title_jp": show.title_jp,
            "year": show.year,
            "top_divide": top_divide_obj
        })
        
    def sort_key(s):
        if s["top_divide"] is not None:
            return abs(s["top_divide"]["divide"])
        return -1.0
        
    results.sort(key=sort_key, reverse=True)
    return results


# ── GET /shows/{slug} ─────────────────────────────────────────────────────────
@router.get("/{slug}", summary="Get a single show by slug")
def get_show(slug: str, db: Session = Depends(get_db)) -> dict:
    """
    Return metadata for a single show identified by its URL-safe slug,
    including detailed topic divide scores and post counts.
    """
    show = db.query(Show).filter(Show.slug == slug).first()
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")
        
    scores = db.query(DivideScore).filter(DivideScore.show_id == show.id).all()
    topics = []
    for s in scores:
        topics.append({
            "topic": s.topic,
            "jp_score": s.jp_avg_score,
            "en_score": s.en_avg_score,
            "divide": s.divide_score,
            "post_count_jp": s.post_count_jp,
            "post_count_en": s.post_count_en
        })
        
    counts = db.query(RawPost.language, func.count(RawPost.id)).filter(RawPost.show_id == show.id).group_by(RawPost.language).all()
    post_count = {"en": 0, "jp": 0}
    for lang, count in counts:
        if lang in post_count:
            post_count[lang] = count
            
    return {
        "slug": show.slug,
        "title_en": show.title_en,
        "title_jp": show.title_jp,
        "mal_id": show.mal_id,
        "year": show.year,
        "post_count": post_count,
        "topics": topics
    }


# ── GET /shows/{slug}/narrative ───────────────────────────────────────────────
@router.get("/{slug}/narrative", summary="Get narrative arc for a show")
def get_narrative(slug: str, db: Session = Depends(get_db)) -> dict:
    """
    Return the generated narrative arc analysis for a show.
    Queries Groq if not cached yet.
    """
    show = db.query(Show).filter(Show.slug == slug).first()
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")
        
    if getattr(show, 'narrative', None):
        return {"narrative": show.narrative}
        
    divide_scores = db.query(DivideScore).filter(DivideScore.show_id == show.id).all()
    if not divide_scores:
        return {"narrative": "Insufficient data to form a narrative summary."}
    
    data_dict = {}
    for d in divide_scores:
        data_dict[d.topic] = {
            "jp_score": d.jp_avg_score,
            "en_score": d.en_avg_score,
            "divide": d.divide_score
        }
        
    data_str = json.dumps(data_dict)
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")
        
    client = Groq(api_key=api_key)
    
    prompt = (
        "You are an anime analyst. Given these sentiment scores comparing Japanese vs English fan communities, "
        "write exactly 2 sentences explaining the cultural divide. Be specific about what each community valued.\n"
        f"Data: {data_str}"
    )
    
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        narrative_text = completion.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM failure: {e}")
        
    show.narrative = narrative_text
    db.commit()
    
    return {"narrative": narrative_text}
