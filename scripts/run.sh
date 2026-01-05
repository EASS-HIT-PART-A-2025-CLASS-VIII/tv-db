#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

usage() {
  cat <<'EOF'
Usage: ./scripts/run.sh <command>

Commands:
  init        Create venv, sync deps, init DB, seed sample data
  back        Run FastAPI backend with reload
  front       Run Streamlit UI (set TV_API_BASE to override API URL)
  test-back   Run backend tests
  test-front  Run Streamlit tests (if tests_streamlit/ exists)
  test-all    Run backend + Streamlit tests
  test        Alias for test-all
  clean       Remove caches and .db files
  help        Show this help
EOF
}

require_uv() {
  if ! command -v uv >/dev/null 2>&1; then
    echo "uv is required but not installed. See https://github.com/astral-sh/uv"
    exit 1
  fi
}

uv_active_flag() {
  local project_env
  project_env="${ROOT_DIR}/.venv"
  if [ -n "${VIRTUAL_ENV:-}" ] && [ "${VIRTUAL_ENV}" != "${project_env}" ]; then
    echo "--active"
  fi
}

cmd_init() {
  require_uv
  if [ ! -d ".venv" ]; then
    uv venv .venv
  fi
  uv sync --all-groups $(uv_active_flag)
  uv run $(uv_active_flag) python -m app.cli init-db
  uv run $(uv_active_flag) python -m app.cli seed
}

cmd_back() {
  require_uv
  uv run $(uv_active_flag) uvicorn app.main:app --reload
}

cmd_front() {
  require_uv
  TV_API_BASE="${TV_API_BASE:-http://localhost:8000}" \
    uv run $(uv_active_flag) streamlit run streamlit_app.py --server.port 8501
}

cmd_test_back() {
  require_uv
  uv run $(uv_active_flag) pytest tests/ -v
}

cmd_test_front() {
  require_uv
  if [ -d "tests_streamlit" ]; then
    uv run $(uv_active_flag) pytest tests_streamlit/ -v
  else
    echo "tests_streamlit/ not found; skipping."
  fi
}

cmd_test_all() {
  cmd_test_back
  cmd_test_front
}

cmd_clean() {
  find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
  find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
  find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
  find . -type f -name "*.db" -delete 2>/dev/null || true
  echo "Cleaned up cache and database files"
}

case "${1:-help}" in
  init) cmd_init ;;
  back) cmd_back ;;
  front) cmd_front ;;
  test-back) cmd_test_back ;;
  test-front) cmd_test_front ;;
  test-all) cmd_test_all ;;
  test) cmd_test_all ;;
  help|-h|--help) usage ;;
  *)
    echo "Unknown command: ${1}"
    usage
    exit 1
    ;;
esac
