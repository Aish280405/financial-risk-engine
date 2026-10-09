from __future__ import annotations
import re
import numpy as np
from app.events import SEVERITY

SOURCE_RELIABILITY = {"GDELT": 0.7, "NewsAPI": 0.8, "Local demo data": 0.55, "manual": 0.5, "Manual": 0.5}
HIGH_RISK_TERMS = [
    "default", "credit loss", "credit losses", "downgrade", "bankruptcy", "debt restructuring", "insolvency",
    "sanction", "sanctions", "recession", "investigation", "fine", "lawsuit", "cyberattack", "data breach",
    "supply disruption", "market selloff", "outage"
]

WEIGHTS = {
    "event_severity": 2.8,
    "sentiment_magnitude": 2.2,
    "source_reliability": 1.0,
    "entity_relevance": 1.0,
    "risk_terms": 2.0,
}


def score_impact(text: str, source: str, event: str, sentiment_score: float, ticker: str | None) -> dict:
    lowered = (text or "").lower()
    risk_hits = [term for term in HIGH_RISK_TERMS if re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", lowered)]

    severity_component = (SEVERITY.get(event, 0.8) / 3.0) * WEIGHTS["event_severity"]
    sentiment_component = min(abs(sentiment_score), 1.0) * WEIGHTS["sentiment_magnitude"]
    source_component = SOURCE_RELIABILITY.get(source, 0.45) * WEIGHTS["source_reliability"]
    entity_component = (1.0 if ticker else 0.45) * WEIGHTS["entity_relevance"]
    risk_component = min(len(risk_hits) / 4, 1.0) * WEIGHTS["risk_terms"]

    raw = 1 + severity_component + sentiment_component + source_component + entity_component + risk_component
    score = float(np.clip(raw, 1, 10))

    explanation = []
    if SEVERITY.get(event, 0) >= 2.5:
        explanation.append("High-severity event category")
    elif event != "Other":
        explanation.append(f"Event category contributes moderate scenario risk: {event}")
    if sentiment_score <= -0.5:
        explanation.append("Strong negative financial sentiment")
    elif sentiment_score >= 0.5:
        explanation.append("Strong positive financial sentiment reduces downside concern")
    elif abs(sentiment_score) > 0.2:
        explanation.append("Meaningful sentiment signal")
    if risk_hits:
        explanation.append("High-risk financial terminology detected: " + ", ".join(risk_hits[:4]))
    if ticker:
        explanation.append("Mapped to a tracked company/exposure")
    explanation.append(f"Source reliability factor applied for {source}")

    return {"impact_score": round(score, 1), "impact_explanation": explanation, "risk_terms": risk_hits}
