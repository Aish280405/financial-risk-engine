from __future__ import annotations
import hashlib
import html
import re
from datetime import datetime, timezone
from typing import Any

from app.entity import extract_entity
from app.events import classify_event
from app.impact import score_impact
from app.sentiment import analyze_sentiment


def preprocess_text(text: str | None) -> str:
    if not text:
        return ""
    cleaned = html.unescape(str(text))
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = re.sub(r"https?://\S+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def article_fingerprint(article: dict[str, Any]) -> str:
    base = f"{article.get('title','')}|{article.get('url','')}|{article.get('text','')}".lower()
    return hashlib.sha256(base.encode("utf-8")).hexdigest()[:16]


def analyze_article(article: dict[str, Any]) -> dict[str, Any]:
    title = preprocess_text(article.get("title", "Untitled")) or "Untitled"
    body = preprocess_text(article.get("text") or article.get("description") or "")
    combined = f"{title}. {body}".strip()
    if not body and title == "Untitled":
        combined = "No article text provided."

    source = article.get("source") or "manual"
    timestamp = article.get("published_at") or article.get("timestamp") or datetime.now(timezone.utc).isoformat()

    entity = extract_entity(combined)
    sentiment = analyze_sentiment(combined)
    event = classify_event(combined)
    impact = score_impact(
        combined,
        source,
        event["event_classification"],
        sentiment["sentiment_score"],
        entity["ticker"],
    )
    confidence = round((sentiment["sentiment_confidence"] + event["event_confidence"] + entity.get("entity_confidence", 0.0)) / 3, 2)

    return {
        "id": article_fingerprint({"title": title, "url": article.get("url", ""), "text": body}),
        "source": source,
        "title": title,
        "text": body,
        "url": article.get("url") or "",
        "entity": entity["entity"],
        "ticker": entity["ticker"],
        "sentiment_score": sentiment["sentiment_score"],
        "sentiment_label": sentiment["sentiment_label"],
        "sentiment_confidence": sentiment["sentiment_confidence"],
        "sentiment_probabilities": sentiment["sentiment_probabilities"],
        "sentiment_model": sentiment["sentiment_model"],
        "sentiment_explanation": sentiment["sentiment_explanation"],
        "event_classification": event["event_classification"],
        "event_confidence": event["event_confidence"],
        "event_evidence": event["event_evidence"],
        "impact_score": impact["impact_score"],
        "impact_explanation": impact["impact_explanation"],
        "risk_terms": impact["risk_terms"],
        "confidence": confidence,
        "timestamp": timestamp,
    }


def analyze_many(articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    signals = []
    for article in articles:
        if not isinstance(article, dict):
            continue
        signal = analyze_article(article)
        if signal["id"] not in seen:
            signals.append(signal)
            seen.add(signal["id"])
    return signals
