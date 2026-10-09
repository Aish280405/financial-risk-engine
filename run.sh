#!/usr/bin/env bash
set -e
python -m uvicorn app.main:app --reload &
API_PID=$!
streamlit run dashboard/app.py
kill $API_PID 2>/dev/null || true
