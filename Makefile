UV_CACHE_DIR ?= $(CURDIR)/.uv-cache

.PHONY: lint format test run

lint:
	UV_CACHE_DIR=$(UV_CACHE_DIR) uv run ruff check .

format:
	UV_CACHE_DIR=$(UV_CACHE_DIR) uv run ruff format .

test:
	UV_CACHE_DIR=$(UV_CACHE_DIR) uv run pytest

run:
	UV_CACHE_DIR=$(UV_CACHE_DIR) uv run ./scripts/start.sh
