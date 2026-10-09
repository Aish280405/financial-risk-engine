from __future__ import annotations
from pathlib import Path
from typing import Any

import pandas as pd

PORTFOLIO_PATH = Path(__file__).resolve().parents[1] / "data" / "portfolio.csv"

SCENARIO_SHOCKS = {
    "Geopolitical": {"equity": -0.10, "bond": -0.05, "loan": -0.05, "derivative": -0.08},
    "Credit Event": {"equity": -0.15, "bond": -0.10, "loan": -0.12, "derivative": -0.08},
    "Macroeconomic": {"equity": -0.08, "bond": -0.05, "loan": -0.04, "derivative": -0.06},
    "Regulatory": {"equity": -0.08, "bond": -0.04, "loan": -0.03, "derivative": -0.05},
    "Operational Risk": {"equity": -0.06, "bond": -0.02, "loan": -0.03, "derivative": -0.03},
    "Market Movement": {"equity": -0.07, "bond": -0.03, "loan": -0.02, "derivative": -0.04},
    "Earnings": {"equity": -0.04, "bond": -0.01, "loan": -0.01, "derivative": -0.01},
    "Merger/Acquisition": {"equity": -0.03, "bond": -0.01, "loan": -0.01, "derivative": -0.01},
    "Product Launch": {"equity": 0.02, "bond": 0.00, "loan": 0.00, "derivative": 0.00},
    "Other": {"equity": -0.02, "bond": -0.01, "loan": -0.01, "derivative": -0.01},
}


def load_portfolio() -> pd.DataFrame:
    return pd.read_csv(PORTFOLIO_PATH)


def portfolio_summary() -> dict[str, Any]:
    df = load_portfolio()
    return {"total_value": float(df["value"].sum()), "positions": df.to_dict(orient="records")}


def run_stress_test(risk_signal: dict[str, Any], threshold: float = 7.0) -> dict[str, Any]:
    df = load_portfolio().copy()
    before = float(df["value"].sum())
    impact = float(risk_signal.get("impact_score", 0) or 0)
    event = risk_signal.get("event_classification", "Other")
    triggered = impact >= threshold

    if not triggered:
        df["shock"] = 0.0
        df["after_value"] = df["value"]
        df["loss"] = 0.0
    else:
        shocks = SCENARIO_SHOCKS.get(event, SCENARIO_SHOCKS["Other"])
        scale = min(max(impact / 10.0, 0.1), 1.0)
        df["shock"] = df["asset_type"].map(shocks).fillna(-0.01) * scale
        if event == "Geopolitical":
            df.loc[df["sector"].str.lower().eq("energy"), "shock"] *= 1.25
        if event == "Credit Event":
            df.loc[df["sensitivity"].str.contains("credit", case=False, na=False), "shock"] *= 1.2
        df["after_value"] = df["value"] * (1 + df["shock"])
        df["loss"] = df["value"] - df["after_value"]

    after = float(df["after_value"].sum())
    loss = before - after
    largest = df.sort_values("loss", ascending=False).head(1).to_dict(orient="records")

    return {
        "triggered": triggered,
        "threshold": threshold,
        "scenario": event if triggered else "No stress test",
        "assumption_note": "Illustrative stress assumptions for the prototype; not regulatory stress-test parameters.",
        "portfolio_value_before": round(before, 2),
        "portfolio_value_after": round(after, 2),
        "absolute_loss": round(loss, 2),
        "percentage_loss": round((loss / before) * 100 if before else 0, 2),
        "asset_impacts": df.to_dict(orient="records"),
        "largest_loss_contributor": largest[0] if largest else None,
        "trigger_explanation": "Impact score met or exceeded threshold." if triggered else "Impact score below configured stress threshold.",
    }
