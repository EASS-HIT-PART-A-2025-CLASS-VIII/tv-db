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
To override the database location, set `DATABASE_URL` (defaults to `sqlite:///./series.db`).
The API exposes:
- `GET /series` — list series
- `POST /series` — create a series entry
- `PUT /series/{id}` — replace a series entry
- `PATCH /series/{id}` — update a series entry
- `DELETE /series/{id}` — delete a series entry

## Streamlit UI
Launch a simple dashboard that talks to the same API:
```bash
# Terminal 1: start the API (defaults to http://localhost:8000)
uv run uvicorn app.main:app --reload

# Terminal 2: start the Streamlit UI (points to the API above)
TV_API_BASE=http://localhost:8000 uv run streamlit run streamlit_app.py --server.port 8501
```
What you get:
- Current series table with total/average rating metrics.
- Quick add form (title, creator, year, optional rating) that posts to `/series`.
- Delete dropdown that calls `DELETE /series/{id}`.
- CSV export button for the visible list.
If you run the API on another host or port, set `TV_API_BASE` accordingly.

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

## Code style
```bash
uv run ruff format .
```

## Docker Compose
```bash
docker compose up --build
```
The compose file maps `series.db` from your workspace into the container so data persists across restarts. The API listens on port 8000 and the Streamlit UI on port 8501. Override `API_PORT`, `STREAMLIT_PORT`, or `DATABASE_URL` via environment variables if needed.

## AI Assistance
This project was developed with assistance from Codex for:
- Linting
- Edge cases
- Documentation
- Test design
