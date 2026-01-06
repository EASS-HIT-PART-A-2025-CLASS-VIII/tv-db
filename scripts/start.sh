#!/usr/bin/env sh
set -eu

API_PORT="${API_PORT:-8000}"
STREAMLIT_PORT="${STREAMLIT_PORT:-8501}"
TV_API_BASE="${TV_API_BASE:-http://127.0.0.1:${API_PORT}}"

export API_PORT
export STREAMLIT_PORT
export TV_API_BASE

trap 'kill 0' INT TERM

uvicorn app.main:app --host 0.0.0.0 --port "${API_PORT}" &
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port "${STREAMLIT_PORT}"
