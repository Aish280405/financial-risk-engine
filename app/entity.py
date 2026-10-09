from __future__ import annotations
import re
from difflib import SequenceMatcher
from typing import Optional

COMPANY_MAP = {
    "AAPL": ["apple", "apple inc", "aapl"],
    "MSFT": ["microsoft", "msft"],
    "NVDA": ["nvidia", "nvda"],
    "AMZN": ["amazon", "amzn"],
    "TSLA": ["tesla", "tsla"],
    "META": ["meta", "facebook", "meta platforms"],
    "GOOGL": ["alphabet", "google", "googl"],
    "JPM": ["jpmorgan", "jp morgan", "jpmorgan chase", "jpm"],
    "BAC": ["bank of america", "bac"],
    "GS": ["goldman sachs", "gs"],
    "XOM": ["exxon", "exxon mobil", "xom"],
    "CVX": ["chevron", "cvx"],
    "WMT": ["walmart", "wmt"],
    "JNJ": ["johnson & johnson", "johnson and johnson", "jnj"],
    "V": ["visa", "v"],
    "MA": ["mastercard", "ma"],
}

DISPLAY_NAMES = {
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "NVIDIA", "AMZN": "Amazon",
    "TSLA": "Tesla", "META": "Meta", "GOOGL": "Alphabet", "JPM": "JPMorgan",
    "BAC": "Bank of America", "GS": "Goldman Sachs", "XOM": "Exxon Mobil",
    "CVX": "Chevron", "WMT": "Walmart", "JNJ": "Johnson & Johnson",
    "V": "Visa", "MA": "Mastercard",
}


def _clean(text: str) -> str:
    return re.sub(r"[^a-z0-9& ]+", " ", text.lower())


def extract_entity(text: str) -> dict:
    cleaned = f" {_clean(text or '')} "
    best: tuple[Optional[str], float] = (None, 0.0)

    for ticker, aliases in COMPANY_MAP.items():
        for alias in aliases:
            alias_clean = _clean(alias).strip()
            if re.search(rf"(?<![a-z0-9]){re.escape(alias_clean)}(?![a-z0-9])", cleaned):
                return {"entity": DISPLAY_NAMES[ticker], "ticker": ticker, "entity_confidence": 0.95}
            for word in cleaned.split():
                score = SequenceMatcher(None, alias_clean, word).ratio()
                if len(alias_clean) > 4 and score > best[1]:
                    best = (ticker, score)

    if best[0] and best[1] >= 0.88:
        return {"entity": DISPLAY_NAMES[best[0]], "ticker": best[0], "entity_confidence": round(best[1], 2)}
    return {"entity": "Market / General", "ticker": None, "entity_confidence": 0.0}
