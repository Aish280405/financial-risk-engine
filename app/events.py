from __future__ import annotations
import re

EVENT_KEYWORDS = {
    "Geopolitical": ["war", "sanction", "sanctions", "military", "conflict", "tariff", "trade restrictions", "shipping route"],
    "Macroeconomic": ["inflation", "interest rate", "fed", "federal reserve", "gdp", "recession", "unemployment"],
    "Credit Event": ["default", "credit loss", "credit losses", "downgrade", "bankruptcy", "debt restructuring", "insolvency"],
    "Merger/Acquisition": ["acquisition", "acquire", "merger", "takeover", "buyout"],
    "Product Launch": ["launch", "unveil", "unveils", "release", "new product"],
    "Regulatory": ["regulator", "regulators", "fine", "lawsuit", "ban", "investigation", "antitrust"],
    "Earnings": ["earnings", "revenue", "profit", "quarter", "guidance", "eps", "margins"],
    "Market Movement": ["shares fell", "shares rose", "stock surged", "stock declined", "market selloff", "equity markets declined"],
    "Operational Risk": ["recall", "outage", "cyberattack", "data breach", "supply disruption", "service disrupted"],
}

VALID_EVENTS = list(EVENT_KEYWORDS.keys()) + ["Other"]
SEVERITY = {
    "Credit Event": 3.0, "Geopolitical": 2.8, "Macroeconomic": 2.5, "Regulatory": 2.2,
    "Operational Risk": 2.0, "Market Movement": 1.8, "Earnings": 1.6,
    "Merger/Acquisition": 1.4, "Product Launch": 1.0, "Other": 0.8,
}


def classify_event(text: str) -> dict:
    lowered = (text or "").lower()
    matches: dict[str, list[str]] = {}
    for event, keywords in EVENT_KEYWORDS.items():
        found = []
        for kw in keywords:
            pattern = re.escape(kw.lower())
            if re.search(rf"(?<![a-z0-9]){pattern}(?![a-z0-9])", lowered):
                found.append(kw)
        if found:
            matches[event] = found

    if not matches:
        return {"event_classification": "Other", "event_confidence": 0.35, "event_evidence": []}

    def rank(item: tuple[str, list[str]]) -> tuple[float, int]:
        event, found = item
        phrase_bonus = sum(1 for kw in found if " " in kw) * 0.4
        return (len(found) + phrase_bonus + SEVERITY[event] * 0.35, len(found))

    event, found = max(matches.items(), key=rank)
    confidence = min(0.9, 0.45 + 0.12 * len(found) + 0.04 * SEVERITY[event])
    return {
        "event_classification": event,
        "event_confidence": round(confidence, 2),
        "event_evidence": found[:5],
    }
