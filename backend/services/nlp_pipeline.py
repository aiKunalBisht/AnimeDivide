import os
import logging
from sqlalchemy.orm import Session
from groq import Groq
from backend.models.database import RawPost, SentimentResult, DivideScore

logger = logging.getLogger(__name__)

TOPIC_KEYWORDS = {
    "ost": ["ost", "soundtrack", "music", "opening", "ending", "op", "ed", "bgm", "song", "track", "音楽", "サントラ", "曲"],
    "animation": ["animation", "visuals", "sakuga", "cgi", "fluid", "作画", "アニメーション", "原画"],
    "story": ["story", "plot", "pacing", "writing", "narrative", "rushed", "ストーリー", "脚本", "展開", "伏線"],
    "characters": ["character", "protagonist", "cast", "development", "キャラ", "主人公", "キャラクター"],
    "faithfulness": ["manga", "source", "faithful", "adaptation", "filler", "原作", "漫画", "改変", "アニオリ"]
}

def detect_topic(text: str) -> str:
    text_lower = text.lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return topic
    return "overall"

def score_sentiment(text: str) -> float:
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.error("GROQ_API_KEY not found in environment")
            return 0.0
            
        client = Groq(api_key=api_key)
        truncated_text = text[:500]
        
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "Return ONLY a float -1.0 to 1.0 for this anime review."},
                {"role": "user", "content": truncated_text}
            ],
            max_tokens=10,
            temperature=0.0
        )
        
        result = completion.choices[0].message.content.strip()
        return float(result)
    except Exception as e:
        logger.error(f"Sentiment scoring failed: {e}")
        return 0.0

def run_pipeline(show_id: int, db: Session) -> dict:
    logger.info(f"Running pipeline for show_id: {show_id}")
    
    # Fetch raw_posts for show_id not yet in sentiment_results
    unprocessed_posts = db.query(RawPost).filter(
        RawPost.show_id == show_id,
        ~RawPost.id.in_(
            db.query(SentimentResult.raw_post_id).filter(SentimentResult.show_id == show_id)
        )
    ).all()
    
    logger.info(f"Found {len(unprocessed_posts)} unprocessed posts")
    
    processed_count = 0
    for post in unprocessed_posts:
        topic = detect_topic(post.text)
        sentiment_score = score_sentiment(post.text)
        
        sr_entry = SentimentResult(
            raw_post_id=post.id,
            show_id=show_id,
            language=post.language,
            topic=topic,
            sentiment_score=sentiment_score
        )
        db.add(sr_entry)
        processed_count += 1
    
    if processed_count > 0:
        db.commit()
        logger.info(f"Successfully inserted {processed_count} sentiment results.")
    
    # Group by topic, compute jp_avg, en_avg, divide_score = jp-en
    all_results = db.query(SentimentResult).filter(SentimentResult.show_id == show_id).all()
    
    topic_stats = {}
    for res in all_results:
        if res.topic not in topic_stats:
            topic_stats[res.topic] = {"jp": [], "en": []}
        topic_stats[res.topic][res.language].append(res.sentiment_score)
    
    topics_summary = {}
    top_divide = {}
    max_divide = -1.0
    
    for topic, stats in topic_stats.items():
        jp_scores = stats["jp"]
        en_scores = stats["en"]
        
        jp_avg = sum(jp_scores) / len(jp_scores) if jp_scores else 0.0
        en_avg = sum(en_scores) / len(en_scores) if en_scores else 0.0
        divide_score = jp_avg - en_avg
        
        topics_summary[topic] = {
            "jp_avg": jp_avg,
            "en_avg": en_avg,
            "divide_score": divide_score,
            "post_count_jp": len(jp_scores),
            "post_count_en": len(en_scores)
        }
        
        # Upsert into divide_scores
        existing = db.query(DivideScore).filter(
            DivideScore.show_id == show_id,
            DivideScore.topic == topic
        ).first()
        
        if existing:
            existing.jp_avg_score = jp_avg
            existing.en_avg_score = en_avg
            existing.divide_score = divide_score
            existing.post_count_jp = len(jp_scores)
            existing.post_count_en = len(en_scores)
        else:
            new_divide = DivideScore(
                show_id=show_id,
                topic=topic,
                jp_avg_score=jp_avg,
                en_avg_score=en_avg,
                divide_score=divide_score,
                post_count_jp=len(jp_scores),
                post_count_en=len(en_scores)
            )
            db.add(new_divide)
        
        # Check max absolute divide for top_divide
        if abs(divide_score) > max_divide:
            max_divide = abs(divide_score)
            top_divide = {topic: topics_summary[topic]}

    db.commit()
    logger.info("Successfully updated divide_scores.")
    
    return {
        "processed": processed_count,
        "topics": topics_summary,
        "top_divide": top_divide
    }
