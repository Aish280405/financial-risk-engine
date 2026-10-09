# Slide 1: Problem + Solution
- Risk teams receive too much unstructured market information.
- The prototype converts news text into structured risk signals.
- Downstream use case: strategic portfolio stress testing.

# Slide 2: Architecture
- Sources: GDELT, NewsAPI, local demo data.
- Pipeline: ingestion → preprocessing → entity → sentiment → event → impact.
- Output feeds portfolio exposure mapping and stress test.

# Slide 3: AI/NLP Risk Engine
- FinBERT financial sentiment when available.
- Rule-based event classifier for transparent taxonomy.
- Company/ticker mapping for reliable MVP entity extraction.
- Fallbacks keep the demo working offline.

# Slide 4: Example Risk Signal
- Entity: Bank of America.
- Event: Credit Event.
- Sentiment: negative, based on financial sentiment probabilities.
- Impact score includes event severity, sentiment, source and risk terms.

# Slide 5: Portfolio Stress Test
- Synthetic $100M wholesale banking portfolio.
- Stress triggers when impact score reaches threshold.
- Scenario shocks are illustrative prototype assumptions.
- Output: before value, after value, loss and asset-level impact.

# Slide 6: Dashboard + Results
- Live risk signals table.
- Selected event explanation.
- Stress trigger result.
- Portfolio before/after chart and largest loss contributor.

# Slide 7: Challenges + Future Work
- Live APIs can be unreliable, so local demo fallback is included.
- Entity extraction is intentionally simple.
- Future work: richer entity coverage, calibrated shocks, historical validation, persistence.
