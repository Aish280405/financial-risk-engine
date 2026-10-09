# Financial Risk Intelligence Engine

Hackathon prototype for Module B: strategic portfolio stress testing. The app converts unstructured market/news text into structured risk signals and uses those signals to run an illustrative portfolio stress test.

This is not a trading system and does not provide financial advice. Impact scores are explainable heuristics, not validated predictions of market losses.

## Problem

Risk teams monitor large volumes of news and market commentary. The challenge is turning messy text into consistent risk signals that can feed a downstream workflow such as portfolio stress testing.

## Solution

The project ingests articles from GDELT, NewsAPI, or local demo data, then runs:

1. text cleanup
2. company/entity extraction
3. financial sentiment with FinBERT, with a keyword fallback
4. event classification using transparent rules
5. explainable risk impact scoring
6. portfolio exposure mapping and stress testing
7. dashboard review

## Architecture

```text
NEWS / SOCIAL DATA
  -> ingestion
  -> preprocessing
  -> entity extraction
  -> financial sentiment
  -> event classification
  -> impact scoring
  -> structured risk signal
  -> portfolio exposure mapping
  -> stress test
  -> dashboard
```

Main files:

- `app/risk_engine.py` orchestrates the pipeline
- `app/ingestion.py` handles GDELT, NewsAPI and local fallback
- `app/sentiment.py` loads FinBERT or falls back to a deterministic keyword method
- `app/events.py` contains the event taxonomy and rules
- `app/impact.py` contains scoring weights and explanations
- `app/stress_test.py` applies portfolio shocks
- `dashboard/app.py` is the Streamlit app
- `app/main.py` is the FastAPI service

## Data sources

Supported sources:

- GDELT public API
- NewsAPI, using `NEWSAPI_KEY` in `.env`
- `data/sample_news.json` local demo data

If a live source fails or returns nothing, the application falls back to local demo data and labels it as `Local demo data`.

## NLP approach

Sentiment uses `ProsusAI/finbert` from HuggingFace. The score is:

```text
positive_probability - negative_probability
```

The output includes positive, neutral and negative probabilities. If the model cannot be downloaded or loaded, a simple keyword sentiment fallback is used. The dashboard shows which sentiment mode was used.

Entity extraction uses a small company/ticker mapping for major public companies. This is intentionally simple for reliability under hackathon constraints.

Event classification is rule-based using the required taxonomy:

- Geopolitical
- Macroeconomic
- Credit Event
- Merger/Acquisition
- Product Launch
- Regulatory
- Earnings
- Market Movement
- Operational Risk
- Other

## Impact scoring methodology

The `Explainable Risk Impact Score` is a deterministic score from 1 to 10. It combines:

- event severity
- sentiment magnitude
- source reliability
- entity relevance
- high-risk financial terms

Weights are centralized in `app/impact.py`. The score is not a trained market-impact model.

## Portfolio stress methodology

The synthetic portfolio is stored in `data/portfolio.csv` and totals $100M:

- Corporate Loans: $25M
- Investment Grade Bonds: $20M
- High Yield Bonds: $15M
- S&P 500 / Equity: $20M
- Energy Equity: $10M
- Interest Rate Swap: $10M

Stress tests trigger automatically when `impact_score >= 7` by default. Scenario shocks are simplified assumptions such as equity, bond, loan and derivative shocks by event type. They are clearly labeled as illustrative prototype assumptions, not regulatory stress-test parameters.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

`NEWSAPI_KEY` is optional. The demo works without it.

## Running locally

API:

```bash
python -m uvicorn app.main:app --reload
```

Dashboard:

```bash
streamlit run dashboard/app.py
```

Or run both with:

```bash
./run.sh
```

## API endpoints

- `GET /health`
- `POST /analyze`
- `GET /portfolio`
- `POST /stress-test`
- `GET /risk-signals`
- `POST /demo/run`

Example:

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{"source":"manual","text":"Bank of America faces credit losses and downgrade risk."}'
```

## Demo mode

Use the sidebar button `Run Demo Event` in Streamlit. It processes curated local articles from `data/sample_news.json`, selects a high-impact event, and shows the article, signal, explanation and stress test.

A strong demo event is the Bank of America credit-loss article because it produces a credit event and triggers the portfolio stress workflow.

## Tests

```bash
pytest
```

## Assumptions and limitations

- Hackathon prototype built for local use on a laptop.
- Live ingestion depends on external API availability.
- GDELT article bodies are not fully scraped; the MVP uses available metadata/snippets.
- FinBERT may need internet on first model download.
- Entity extraction is mapping-based and will miss companies outside the list.
- Impact score and stress shocks are explainable assumptions, not validated forecasts.

## Future improvements

- Better article body extraction for live sources.
- More complete company/entity universe.
- Calibrated impact scoring using historical events.
- Sector-specific and geography-specific stress mappings.
- Persistent storage for signal history.
