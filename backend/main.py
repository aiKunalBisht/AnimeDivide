"""
main.py
=======
FastAPI application entry point for the AnimeDivide backend.

Run with:
    uvicorn backend.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import shows, scraper, pipeline

app = FastAPI(
    title="AnimeDivide API",
    description="Anime narrative analysis — scraping, processing, and story-arc endpoints.",
    version="0.1.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(shows.router,   prefix="/shows",    tags=["Shows"])
app.include_router(scraper.router, prefix="/scrape",   tags=["Scraper"])
app.include_router(pipeline.router,prefix="/pipeline", tags=["Pipeline"])


# ── Root health check ─────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root() -> dict:
    return {"status": "ok", "service": "AnimeDivide API", "version": "0.1.0"}
