# 5-minute demo script

## 0:00–0:40 — Problem
Explain that risk teams need to turn unstructured market news into consistent risk signals. This project focuses on financial risk intelligence and scenario analysis, not trading advice.

## 0:40–1:20 — Show incoming article
Open the Streamlit dashboard. In the sidebar keep `Demo data` selected and click `Run Demo Event`. Select the Bank of America credit-loss article if it is not already selected.

## 1:20–2:10 — Show NLP risk signal
Walk through entity, event classification, sentiment score and confidence. Point out whether FinBERT or the fallback sentiment method is being used. Expand the article text and show the event evidence.

## 2:10–3:20 — Show high-impact event triggering stress test
Show the impact score and the `Why this score?` section. Explain that the score is an explainable heuristic using event severity, sentiment, source reliability, entity relevance and risk terms. Because the score is above the threshold, the stress test is triggered.

## 3:20–4:10 — Show portfolio impact
Review before value, after value, absolute loss and loss percentage. Show the bar chart and largest loss contributor. Mention that the portfolio is a synthetic $100M wholesale banking portfolio.

## 4:10–5:00 — Architecture, limitations and future work
Summarize the pipeline: sources → NLP risk engine → structured signal → stress test → dashboard. State limitations: live API dependency, simple entity extraction, heuristic impact scoring and illustrative stress assumptions. Close with future improvements around calibration and broader entity coverage.
