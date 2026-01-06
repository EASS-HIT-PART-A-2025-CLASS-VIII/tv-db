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
If you hit uv cache permission issues in restricted environments, set:
```bash
export UV_CACHE_DIR="$(pwd)/.uv-cache"
```

## Makefile shortcuts
```bash
make run
make test
make lint
make format
```

## Run the API locally
```bash
uv run uvicorn app.main:app --reload
```
The lifespan handler initializes the SQLite database file on startup, so no manual migration step is needed for development.
To override the database location, set `DATABASE_URL` (defaults to `sqlite:///./series.db`). The database file is created on first run.
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
Initialize or seed the database (no `.db` files are checked in; the file appears after the first run):
```bash
uv run python -m app.cli init-db
uv run python -m app.cli seed  # adds 3 sample TV series
```

## Tests
```bash
uv run pytest
```
Or via Make:
```bash
make test
```

## Code style
```bash
uv run ruff format .
```
Lint:
```bash
uv run ruff check .
```
Or via Make:
```bash
make format
make lint
```

## Docker Compose
```bash
mkdir -p data
docker compose up --build
```
The compose file maps `./data` into the container so data persists across restarts (`./data/series.db`). The API listens on port 8000 and the Streamlit UI on port 8501. Override `API_PORT`, `STREAMLIT_PORT`, or `DATABASE_URL` via environment variables if needed. The container defaults `TV_API_BASE` to `http://127.0.0.1:${API_PORT}` unless you override it.

## AI Assistance
This project was developed with assistance from Codex for:
- Linting
- Edge cases
- Documentation
- Test design
