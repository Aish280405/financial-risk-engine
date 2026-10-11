from __future__ import annotations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from app.ingestion import get_articles, load_local_sample
from app.risk_engine import analyze_article, analyze_many
from app.stress_test import portfolio_summary, run_stress_test

load_dotenv()

st.set_page_config(page_title="Financial Risk Intelligence Engine", layout="wide")
st.markdown("""
<style>
/* Theme comes from .streamlit/config.toml (light theme).
   Only light touch-ups here — no aggressive overrides. */
.block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

if "signals" not in st.session_state:
    st.session_state.signals = []
if "selected_signal" not in st.session_state:
    st.session_state.selected_signal = None

st.title("Financial Risk Intelligence Engine")
st.caption("Unstructured market information → structured risk signals → portfolio stress")

with st.sidebar:
    st.header("Controls")
    source = st.selectbox("Data source", ["Demo data", "GDELT", "NewsAPI"])
    threshold = st.slider("Risk threshold", 1.0, 10.0, 7.0, 0.5)
    total = portfolio_summary()["total_value"]
    st.metric("Portfolio value", f"${total/1_000_000:.0f}M")
    if st.button("Run Demo Event", use_container_width=True):
        articles, actual_source = get_articles(source, limit=8)
        st.session_state.signals = analyze_many(articles)
        st.session_state.selected_signal = max(st.session_state.signals, key=lambda s: s["impact_score"]) if st.session_state.signals else None
        st.session_state.actual_source = actual_source
    st.divider()
    st.caption("Demo Mode — Local Sample Data is used whenever live APIs are unavailable.")

st.subheader("Live Risk Signals")
if not st.session_state.signals:
    articles = load_local_sample(8)
    st.session_state.signals = analyze_many(articles)
    st.session_state.selected_signal = max(st.session_state.signals, key=lambda s: s["impact_score"])
    st.session_state.actual_source = "Local demo data"

signals_df = pd.DataFrame(st.session_state.signals)
filter_cols = st.columns(3)
with filter_cols[0]:
    event_filter = st.multiselect("Event type", sorted(signals_df["event_classification"].unique()))
with filter_cols[1]:
    source_filter = st.multiselect("Source", sorted(signals_df["source"].unique()))
with filter_cols[2]:
    company_filter = st.multiselect("Company", sorted(signals_df["entity"].unique()))

view_df = signals_df.copy()
if event_filter:
    view_df = view_df[view_df["event_classification"].isin(event_filter)]
if source_filter:
    view_df = view_df[view_df["source"].isin(source_filter)]
if company_filter:
    view_df = view_df[view_df["entity"].isin(company_filter)]

show_cols = ["timestamp", "source", "entity", "event_classification", "sentiment_score", "impact_score"]
st.dataframe(view_df[show_cols].rename(columns={"timestamp": "Time", "source": "Source", "entity": "Entity", "event_classification": "Event", "sentiment_score": "Sentiment", "impact_score": "Impact"}), use_container_width=True, hide_index=True)

if not view_df.empty:
    titles = view_df["title"].tolist()
    selected_title = st.selectbox("Select event", titles, index=0)
    st.session_state.selected_signal = next(s for s in st.session_state.signals if s["title"] == selected_title)

signal = st.session_state.selected_signal
st.divider()
st.subheader("Selected Event")
if signal:
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Company", signal["entity"])
    c2.metric("Event", signal["event_classification"])
    c3.metric("Sentiment", f"{signal['sentiment_score']:+.2f}")
    c4.metric("Impact", f"{signal['impact_score']:.1f}/10")
    c5.metric("Confidence", f"{signal['confidence']:.2f}")
    c6.metric("Source", signal["source"])

    with st.expander("Article", expanded=True):
        st.write(f"**{signal['title']}**")
        st.write(signal["text"])
        if signal.get("url"):
            st.caption(signal["url"])

    st.markdown("**Why this score?**")
    for item in signal["impact_explanation"]:
        st.write(f"+ {item}")
    st.caption(signal["sentiment_explanation"])
    if signal.get("event_evidence"):
        st.caption("Event evidence: " + ", ".join(signal["event_evidence"]))

    st.divider()
    st.subheader("Stress Test")
    stress = run_stress_test(signal, threshold)
    if stress["triggered"]:
        st.error("HIGH IMPACT EVENT DETECTED — stress test triggered")
    else:
        st.info("No stress test triggered. Impact score below configured stress threshold.")

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Before", f"${stress['portfolio_value_before']/1_000_000:.1f}M")
    s2.metric("After", f"${stress['portfolio_value_after']/1_000_000:.1f}M")
    s3.metric("Loss", f"${stress['absolute_loss']/1_000_000:.1f}M")
    s4.metric("Loss %", f"{stress['percentage_loss']:.2f}%")
    st.caption(stress["assumption_note"])

    st.subheader("Portfolio Impact")
    impacts = pd.DataFrame(stress["asset_impacts"])
    chart_df = impacts.groupby("asset_type")[["value", "after_value"]].sum().rename(columns={"value": "Before", "after_value": "After"})
    st.bar_chart(chart_df)
    largest = stress.get("largest_loss_contributor") or {}
    if largest:
        st.write(f"Largest loss contributor: **{largest.get('asset_name')}** (${largest.get('loss', 0)/1_000_000:.2f}M)")
    st.dataframe(impacts[["asset_name", "asset_type", "value", "shock", "after_value", "loss"]], use_container_width=True, hide_index=True)

st.divider()
st.subheader("Analyze an article")
manual_text = st.text_area("Paste arbitrary financial text", height=130)
manual_title = st.text_input("Optional title", "Manual article")
if st.button("Analyze Risk") and manual_text.strip():
    manual_signal = analyze_article({"source": "manual", "title": manual_title, "text": manual_text})
    st.session_state.signals.insert(0, manual_signal)
    st.session_state.selected_signal = manual_signal
    st.rerun()

st.divider()
st.subheader("Event History")
st.dataframe(pd.DataFrame(st.session_state.signals)[show_cols], use_container_width=True, hide_index=True)
