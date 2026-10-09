from __future__ import annotations
from typing import Any, Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from app.ingestion import get_articles
from app.risk_engine import analyze_article, analyze_many
from app.stress_test import portfolio_summary, run_stress_test

load_dotenv()

app = FastAPI(title="Financial Risk Intelligence Engine", version="0.1.0")
RISK_SIGNALS: list[dict[str, Any]] = []


class AnalyzeRequest(BaseModel):
    text: str
    source: str = "manual"
    title: Optional[str] = "Manual article"
    url: Optional[str] = ""


class StressRequest(BaseModel):
    risk_signal: dict[str, Any]
    threshold: float = 7.0


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "service": "financial-risk-engine"}


@app.post("/analyze")
def analyze(req: AnalyzeRequest) -> dict[str, Any]:
    signal = analyze_article({"source": req.source, "title": req.title, "text": req.text, "url": req.url})
    RISK_SIGNALS.insert(0, signal)
    return signal


@app.get("/portfolio")
def portfolio() -> dict[str, Any]:
    return portfolio_summary()


@app.post("/stress-test")
def stress_test(req: StressRequest) -> dict[str, Any]:
    return run_stress_test(req.risk_signal, req.threshold)


@app.get("/risk-signals")
def risk_signals() -> list[dict[str, Any]]:
    return RISK_SIGNALS[:50]


@app.post("/demo/run")
def demo_run(source: str = "Demo data", limit: int = 8, threshold: float = 7.0) -> dict[str, Any]:
    articles, actual_source = get_articles(source, limit)
    signals = analyze_many(articles)
    for signal in reversed(signals):
        RISK_SIGNALS.insert(0, signal)
    selected = max(signals, key=lambda s: s["impact_score"]) if signals else None
    stress = run_stress_test(selected, threshold) if selected else None
    return {"requested_source": source, "actual_source": actual_source, "signals": signals, "selected_signal": selected, "stress_test": stress}
