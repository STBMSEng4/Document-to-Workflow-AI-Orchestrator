#!/usr/bin/env bash
# SpecFlow AI — Launch Streamlit (macOS / Linux)
# Run from repo root: bash scripts/run_streamlit.sh
cd "$(dirname "$0")/.."
streamlit run app/ui/streamlit_app.py
