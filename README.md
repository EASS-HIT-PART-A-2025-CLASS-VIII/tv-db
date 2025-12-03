# FastAPI TV Series Catalogue (EX1)

Small FastAPI service for a TV series catalogue using SQLModel + SQLite. Includes Typer CLI helpers, CRUD API, and pytest coverage.

## Requirements
- Python 3.11+
- [uv](https://github.com/astral-sh/uv)

## Setup
```bash
cd tv-db
uv venv .venv
source .venv/bin/activate
uv sync --all-groups
```

## Run the API locally
```bash
uv run uvicorn app.main:app --reload
```
The lifespan handler initializes the SQLite database file on startup, so no manual migration step is needed for development.
The API exposes:
- `GET /series` — list series
- `POST /series` — create a series entry
- `DELETE /series/{id}` — delete a series entry

## Typer CLI
Initialize or seed the database (no `.db` files are checked in):
```bash
uv run python -m app.cli init-db
uv run python -m app.cli seed  # adds 3 sample TV series
```

## Tests
```bash
uv run pytest
```

## Docker Compose
```bash
docker compose up --build
```
The compose file maps `series.db` from your workspace into the container so data persists across restarts. The API listens on port 9000.

## AI Assistance
This project was developed with assistance from Codex for:
- Linting
- Edge cases
- Documentation
- Test design
