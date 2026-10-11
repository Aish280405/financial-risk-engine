# [Project Title] - S&P Global & Crisil Campus Hackathon

**Candidate Name:** Aishwarya Sinha
**College Email ID:** aishwarya.23fe10cai00591@muj.manipal.edu
**College / Campus:** Manipal University Jaipur
**Demo Video Link:** [YouTube / Unlisted]
**Slide Deck Link (if hosted externally):**

## 1. Project Overview / Problem Statement & Approach

Risk teams monitor large volumes of news and market commentary. The challenge is turning messy text into consistent risk signals that can feed a downstream workflow such as portfolio stress testing. This project addresses that problem by automating the ingestion of unstructured market news via GDELT and NewsAPI, extracting financial entities, computing sentiment with FinBERT (with a keyword fallback), classifying events using rule-based taxonomy, and scoring explainable risk impact. These structured signals are then mapped to a synthetic portfolio and used to run illustrative stress tests, demonstrating how news-driven events can affect portfolio value.

The approach follows a pipeline architecture: NEWS / SOCIAL DATA → ingestion → preprocessing → entity extraction → financial sentiment → event classification → impact scoring → portfolio exposure mapping → stress test → dashboard review. All components are implemented as a FastAPI backend with a Streamlit frontend, relying on local demo data as fallback when live APIs are unavailable.

## 2. Architecture & Tech Stack

**System design and data flow:**

```text
NEWS / SOCIAL DATA
  -> ingestion
  -> preprocessing
  -> entity extraction
  -> financial sentiment (FinBERT / keyword fallback)
  -> event classification (rule-based taxonomy)
  -> explainable risk impact scoring
  -> structured risk signal
  -> portfolio exposure mapping
  -> stress test
  -> dashboard
```

**Key frameworks, libraries, and AI/ML tools:**

- **FastAPI** – REST API service (`app/main.py`)
- **Streamlit** – Interactive dashboard (`dashboard/app.py`)
- **Transformers / PyTorch** – FinBERT model for financial sentiment (`app/sentiment.py`)
- **Pandas / NumPy** – Data manipulation and portfolio calculations
- **Requests / Feedparser** – GDELT and RSS API integration (`app/ingestion.py`)
- **Pydantic** – Request validation for API endpoints
- **Scikit-learn** – Supporting ML utilities
- **Environment management** – `.env` with `NEWSAPI_KEY` and `FINBERT_MODEL`

## 3. Dataset Used

- **Source/nature**: The system ingests unstructured financial news from three sources: (1) GDELT public API, (2) NewsAPI (requires `NEWSAPI_KEY`), and (3) a local demo dataset (`data/sample_news.json`) containing 8 curated financial news articles. The local dataset serves as a fallback when live APIs fail or are rate-limited.
- **Assumptions**: 
  - GDELT article bodies are available via metadata/snippets; full-text scraping is not performed.
  - FinBERT may require internet access for first-time model download; a keyword-based fallback is included for offline reliability.
  - Entity extraction uses a mapping of 28 major public companies/tickers; companies outside this list are labeled "Market / General".
  - Impact scores and stress-shock assumptions are explainable heuristics, not validated financial forecasts.
  - The evaluation dataset (`data/evaluation/all-data.csv`, Financial PhraseBank) is separate from live ingestion and used only for external model evaluation.

## 4. Quickstart & Installation

**Runtime:** Python 3.11 on macOS (tested with Python 3.9+.)

**Step-by-step commands:**

```bash
git clone <your-repo-url>
cd <repo-folder>
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set NEWSAPI_KEY if desired
```

**Running the services:**

```bash
# API (FastAPI)
python -m uvicorn app.main:app --reload

# Dashboard (Streamlit)
streamlit run dashboard/app.py

# Both together
./run.sh
```

**API endpoints (base URL: `http://127.0.0.1:8000`):**

- `GET /health`
- `POST /analyze` – `{ "text": "...", "source": "manual" | "newsapi" | "gdelt", ... }`
- `GET /portfolio`
- `POST /stress-test`
- `GET /risk-signals`
- `POST /demo/run`

## 5. Key Results & Domain Impact

**What the prototype demonstrates:**

- End-to-end pipeline converting unstructured financial news into structured risk signals (entity, sentiment, event classification, impact score 1‑10).
- Automatic stress‑test triggering when `impact_score >= 7`, showing before/after portfolio values, absolute and percentage loss, and per‑asset impact.
- Visual portfolio impact chart and largest-loss contributor identification via Streamlit.
- Working demo: the “Bank of America credit-loss” article from local data produces a credit event, impact score > 7, and triggers the stress test, illustrating the full workflow.

**Why it matters from a use‑case standpoint:**

- Risk teams receive vast amounts of market commentary; this prototype shows how NLP can distill that noise into a handful of explainable risk signals.
- The structured signals can feed downstream workflows such as portfolio stress testing, scenario analysis, and monitoring of high‑impact events.
- The modular architecture (ingestion → NLP → impact → stress test) is extensible: additional data sources, refined entity mapping, or calibrated shock tables can be swapped in without rewriting the core pipeline.
- The hack‑prototype demonstrates that AI/NLP tools are accessible for risk‑management prototyping under hackathon constraints (synthetic portfolio, explainable heuristics, local‑first fallback).

---

## Model Evaluation 

**FinBERT** is a pretrained financial‑sentiment model from HuggingFace (`ProsusAI/finbert`). It produces a sentiment score as `positive_probability - negative_probability`, clipped to the range [-1, 1], along with probabilities for positive, neutral, and negative classes. The existing `app/sentiment.py` uses FinBERT by default, with a keyword‑based fallback for reliability when the model cannot be loaded.

**Evaluation dataset**: The Financial PhraseBank dataset (Kaggle, `ankurzing/sentiment-analysis-for-financial-news`, CC‑BY‑NC‑SA‑4.0) was downloaded and placed in `data/evaluation/all-data.csv`. It contains 4,845 financial news headlines labeled as positive, neutral, or negative, originally compiled by Malo et al. (2014). The dataset is **not** used for live ingestion or demo input; it is solely for external model evaluation.

**Reported metrics** (evaluation run on full 4,845‑sample dataset):
- Overall accuracy: 0.889 (4,308 / 4,846)
- Per‑class performance:
  - **Positive**: precision 0.810, recall 0.919, F1 0.861
  - **Neutral**: precision 0.961, recall 0.858, F1 0.907
  - **Negative**: precision 0.801, recall 0.969, F1 0.877
- Confusion matrix available in `scripts/evaluate_sentiment.py`

**Separation from live ingestion**: The evaluation dataset resides in `data/evaluation/` and is never passed to the ingestion, risk engine, or dashboard modules. The pipeline continues to use FinBERT (or its keyword fallback) for live analysis without retraining or refitting on this external dataset.

## Future improvements

- Better article body extraction for live sources.
- More complete company/entity universe.
- Calibrated impact scoring using historical events.
- Sector‑specific and geography‑specific stress mappings.
- Persistent storage for signal history.