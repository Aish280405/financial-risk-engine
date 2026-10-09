from __future__ import annotations
import os
from functools import lru_cache
from typing import Any

import numpy as np

POSITIVE_WORDS = {"beat", "strong", "improved", "rose", "surged", "positive", "growth", "profit", "higher demand", "stable"}
NEGATIVE_WORDS = {"loss", "losses", "default", "downgrade", "bankruptcy", "risk", "decline", "declined", "sanction", "sanctions", "inflation", "recession", "fine", "lawsuit", "outage", "breach", "disruption", "fell"}


@lru_cache(maxsize=1)
def _load_finbert() -> Any:
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

    model_name = os.getenv("FINBERT_MODEL", "ProsusAI/finbert")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    return pipeline("text-classification", model=model, tokenizer=tokenizer, top_k=None, truncation=True, max_length=512)


def _fallback_sentiment(text: str) -> dict:
    lowered = (text or "").lower()
    pos = sum(1 for word in POSITIVE_WORDS if word in lowered)
    neg = sum(1 for word in NEGATIVE_WORDS if word in lowered)
    raw = (pos - neg) / max(pos + neg, 1)
    score = float(np.clip(raw, -1, 1))
    positive = max(score, 0) * 0.55 + 0.15
    negative = max(-score, 0) * 0.55 + 0.15
    neutral = max(0.05, 1 - positive - negative)
    total = positive + negative + neutral
    probs = {"positive": positive / total, "negative": negative / total, "neutral": neutral / total}
    label = "Positive" if score > 0.15 else "Negative" if score < -0.15 else "Neutral"
    return {
        "sentiment_score": round(score, 3),
        "sentiment_label": label,
        "sentiment_confidence": round(max(probs.values()), 3),
        "sentiment_probabilities": {k: round(v, 3) for k, v in probs.items()},
        "sentiment_model": "fallback_keyword",
        "sentiment_explanation": f"Fallback keyword method found {pos} positive and {neg} negative finance terms.",
    }


def analyze_sentiment(text: str) -> dict:
    if not (text or "").strip():
        return _fallback_sentiment(text)
    if os.getenv("FINBERT_DISABLE", "").lower() in {"1", "true", "yes"}:
        return _fallback_sentiment(text)
    try:
        pipe = _load_finbert()
        results = pipe(text[:3000])[0]
        probs = {item["label"].lower(): float(item["score"]) for item in results}
        positive = probs.get("positive", 0.0)
        negative = probs.get("negative", 0.0)
        neutral = probs.get("neutral", 0.0)
        score = positive - negative
        label_key = max(probs, key=probs.get)
        return {
            "sentiment_score": round(score, 3),
            "sentiment_label": label_key.capitalize(),
            "sentiment_confidence": round(probs[label_key], 3),
            "sentiment_probabilities": {"positive": round(positive, 3), "neutral": round(neutral, 3), "negative": round(negative, 3)},
            "sentiment_model": "FinBERT",
            "sentiment_explanation": f"FinBERT probability balance: positive {positive:.2f}, neutral {neutral:.2f}, negative {negative:.2f}.",
        }
    except Exception as exc:
        result = _fallback_sentiment(text)
        result["sentiment_error"] = str(exc)[:180]
        return result
