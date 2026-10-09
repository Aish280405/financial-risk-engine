from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import feedparser
except Exception:  # optional until requirements are installed
    feedparser = None

try:
    import requests
except Exception:  # optional until requirements are installed
    requests = None

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_news.json"


def _normalize(source: str, title: str | None, text: str | None, url: str | None, published_at: str | None) -> dict[str, str]:
    return {
        "source": source,
        "title": (title or "Untitled").strip(),
        "text": (text or title or "").strip(),
        "url": url or "",
        "published_at": published_at or datetime.now(timezone.utc).isoformat(),
    }


def _dedupe(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    out = []
    for item in records:
        key = (item.get("title", "").lower(), item.get("url", ""))
        if item.get("title") and key not in seen:
            out.append(item)
            seen.add(key)
    return out


def load_local_sample(limit: int | None = None) -> list[dict[str, Any]]:
    with DATA_PATH.open() as f:
        data = json.load(f)
    normalized = [_normalize(x.get("source", "Local demo data"), x.get("title"), x.get("text"), x.get("url"), x.get("published_at")) for x in data]
    return normalized[:limit] if limit else normalized


def fetch_gdelt(query: str = "finance risk OR credit OR inflation OR earnings", limit: int = 10) -> list[dict[str, Any]]:
    if requests is None:
        return []
    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    params = {"query": query, "mode": "ArtList", "format": "json", "maxrecords": limit, "sort": "HybridRel"}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        articles = resp.json().get("articles", [])
        records = []
        for a in articles:
            records.append(_normalize("GDELT", a.get("title"), a.get("seendate") and a.get("title"), a.get("url"), a.get("seendate")))
        return _dedupe(records)
    except Exception:
        return []


def fetch_newsapi(query: str = "financial risk OR credit loss OR inflation OR earnings", limit: int = 10) -> list[dict[str, Any]]:
    if requests is None:
        return []
    key = os.getenv("NEWSAPI_KEY")
    if not key:
        return []
    try:
        resp = requests.get(
            "https://newsapi.org/v2/everything",
            params={"q": query, "language": "en", "sortBy": "publishedAt", "pageSize": limit, "apiKey": key},
            timeout=10,
        )
        resp.raise_for_status()
        records = []
        for a in resp.json().get("articles", []):
            text = " ".join(part for part in [a.get("description"), a.get("content")] if part)
            records.append(_normalize("NewsAPI", a.get("title"), text, a.get("url"), a.get("publishedAt")))
        return _dedupe(records)
    except Exception:
        return []


def fetch_rss_fallback(limit: int = 10) -> list[dict[str, Any]]:
    # Lightweight secondary public feed fallback for development when JSON APIs are unavailable.
    if feedparser is None:
        return []
    try:
        feed = feedparser.parse("https://feeds.finance.yahoo.com/rss/2.0/headline?s=AAPL,MSFT,JPM,BAC,XOM,NVDA&region=US&lang=en-US")
        records = []
        for entry in feed.entries[:limit]:
            records.append(_normalize("GDELT", entry.get("title"), entry.get("summary"), entry.get("link"), entry.get("published")))
        return _dedupe(records)
    except Exception:
        return []


def get_articles(source: str = "Demo data", limit: int = 10) -> tuple[list[dict[str, Any]], str]:
    source = (source or "Demo data").lower()
    if source == "gdelt":
        records = fetch_gdelt(limit=limit) or fetch_rss_fallback(limit=limit)
        return (records, "GDELT") if records else (load_local_sample(limit), "Local demo data")
    if source == "newsapi":
        records = fetch_newsapi(limit=limit)
        return (records, "NewsAPI") if records else (load_local_sample(limit), "Local demo data")
    return load_local_sample(limit), "Local demo data"
