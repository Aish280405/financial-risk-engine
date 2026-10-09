from __future__ import annotations
import os

os.environ["FINBERT_DISABLE"] = "1"

from app.events import VALID_EVENTS, classify_event
from app.risk_engine import analyze_article
from app.stress_test import portfolio_summary, run_stress_test


def test_sentiment_score_range():
    signal = analyze_article({"source": "Local demo data", "title": "Bank default risk", "text": "Bank of America faces credit losses and default risk."})
    assert -1 <= signal["sentiment_score"] <= 1


def test_impact_score_range():
    signal = analyze_article({"source": "manual", "title": "Inflation", "text": "Inflation and recession risk increased."})
    assert 1 <= signal["impact_score"] <= 10


def test_event_classifier_valid_category():
    result = classify_event("The company reported earnings, revenue and guidance for the quarter.")
    assert result["event_classification"] in VALID_EVENTS


def test_stress_test_threshold():
    low = {"impact_score": 4.0, "event_classification": "Credit Event"}
    high = {"impact_score": 8.0, "event_classification": "Credit Event"}
    assert run_stress_test(low, threshold=7)["triggered"] is False
    assert run_stress_test(high, threshold=7)["triggered"] is True


def test_portfolio_value():
    assert portfolio_summary()["total_value"] == 100_000_000


def test_malformed_article_does_not_crash():
    signal = analyze_article({"bad": None})
    assert signal["title"] == "Untitled"
    assert 1 <= signal["impact_score"] <= 10
