"""
mal_scraper.py
==============
Scrape MyAnimeList reviews for a given anime and persist them to `raw_posts`.

Public API
----------
    scrape_reviews(mal_id, show_id) -> list[dict]
    save_reviews(reviews, db)       -> int          # count of newly inserted rows
"""

import hashlib
import logging
import time
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup
from langdetect import detect, LangDetectException
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.models.database import RawPost

log = logging.getLogger(__name__)

# ── Helpers ────────────────────────────────────────────────────────────────────

def _md5(text: str) -> str:
    """Return the hex MD5 digest of *text* (UTF-8 encoded)."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def _detect_language(text: str) -> str | None:
    """
    Detect the language of *text* using langdetect.

    Returns
    -------
    "en", "jp", or None (if unrecognised / undesired language).
    """
    try:
        lang = detect(text)
    except LangDetectException:
        return None

    if lang == "en":
        return "en"
    if lang == "ja":
        return "jp"          # normalise "ja" → "jp" for project consistency
    return None              # skip other languages

# ── Core scraping function ────────────────────────────────────────────────────

def scrape_reviews(mal_id: int, show_id: int) -> list[dict]:
    """
    Scrape reviews for anime *mal_id* directly from the MAL site.

    Parameters
    ----------
    mal_id : int
        MyAnimeList anime ID.
    show_id : int
        Local database ``shows.id`` — attached to every review dict.

    Returns
    -------
    list[dict]
        Each dict has the keys expected by :class:`RawPost`.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,ja;q=0.8"
    }

    reviews: list[dict] = []
    
    with httpx.Client(timeout=30.0) as client:
        for page in range(1, 6):
            url = f"https://myanimelist.net/anime/{mal_id}/reviews?p={page}"
            log.info("GET %s", url)

            try:
                resp = client.get(url, headers=headers)
                resp.raise_for_status()
            except httpx.RequestError as exc:
                log.error("Request failed for %s: %s", url, exc)
                if page < 5:
                    time.sleep(2)
                continue
            except httpx.HTTPStatusError as exc:
                log.error("HTTP error for %s: %s", url, exc)
                if page < 5:
                    time.sleep(2)
                continue

            soup = BeautifulSoup(resp.text, 'lxml')
            review_elements = soup.select('div.review-element')
            
            if not review_elements:
                log.info("No reviews found on page %d for mal_id=%d. Stopping pagination.", page, mal_id)
                break
                
            page_review_count = 0
            
            for review_el in review_elements:
                text_div = review_el.select_one('div.text')
                if not text_div:
                    continue
                body = text_div.get_text(separator=' ', strip=True)
                if not body:
                    continue
                    
                lang = _detect_language(body)
                if lang is None:
                    continue
                    
                username = "anonymous"
                username_div = review_el.select_one('div.username')
                if username_div:
                    a_tag = username_div.select_one('a')
                    if a_tag and a_tag.text:
                        username = a_tag.text.strip()
                    else:
                        username = username_div.get_text(strip=True)
                        
                score = None
                score_div = review_el.select_one('div.score span.num')
                if score_div:
                    try:
                        parsed_score = int(score_div.text.strip())
                        if 1 <= parsed_score <= 10:
                            score = parsed_score
                    except ValueError:
                        pass
                        
                reviews.append({
                    "show_id":    show_id,
                    "source":     f"mal_{lang}",       # "mal_en" or "mal_jp"
                    "language":   lang,
                    "username":   username,
                    "text":       body,
                    "score":      score,
                    "scraped_at": datetime.now(timezone.utc),
                    "post_hash":  _md5(body),
                })
                page_review_count += 1
                
            log.info("Scraped %d usable reviews from page %d", page_review_count, page)
            
            if page < 5:
                time.sleep(2)

    log.info("Scraped a total of %d usable reviews (en/jp) for mal_id=%d.", len(reviews), mal_id)
    return reviews


# ── Persistence ───────────────────────────────────────────────────────────────

def save_reviews(reviews: list[dict], db: Session) -> int:
    """
    Insert reviews into ``raw_posts``, skipping duplicates by ``post_hash``.

    Returns
    -------
    int
        Number of newly inserted rows.
    """
    if not reviews:
        return 0

    inserted = 0

    for rev in reviews:
        # Deduplication: skip if hash already exists
        exists = db.execute(
            text("SELECT 1 FROM raw_posts WHERE post_hash = :h LIMIT 1"),
            {"h": rev["post_hash"]},
        ).fetchone()

        if exists:
            continue

        post = RawPost(
            show_id    = rev["show_id"],
            source     = rev["source"],
            language   = rev["language"],
            username   = rev["username"],
            text       = rev["text"],
            score      = rev["score"],
            scraped_at = rev["scraped_at"],
            post_hash  = rev["post_hash"],
        )
        db.add(post)

        try:
            db.flush()
            inserted += 1
        except Exception as exc:
            db.rollback()
            log.error("Failed to insert post_hash=%s: %s", rev["post_hash"], exc)

    db.commit()
    log.info("Inserted %d new posts out of %d scraped.", inserted, len(reviews))
    return inserted
