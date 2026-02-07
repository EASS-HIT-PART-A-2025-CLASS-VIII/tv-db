# EX3 Notes

## Orchestration overview
- API + Streamlit run in the `api` service (FastAPI + UI).
- Redis is the shared queue/trace store.
- `worker` consumes Redis jobs and posts reports back to the API.
- Ollama runs locally and powers AI summaries via the API.

## Async refresh (Session 09)
- `scripts/refresh.py` pulls `/series`, refreshes each entry via `/series/{id}/refresh`.
- Bounded concurrency via `asyncio.Semaphore`.
- Retries with exponential backoff in `_with_retries`.
- Redis idempotency keys: `refresh:{series_id}:{YYYY-MM-DD}` (TTL 24h).
- Trace stream: `tvdb:refresh:trace` (Redis `XADD` entries).

Trace excerpt (sample):
```
1) 1737051645123-0
2) 1) "series_id"
   2) "7"
   3) "status"
   4) "refreshed"
   5) "timestamp"
   6) "2026-01-24T18:02:20.123456+00:00"
```

## Telemetry + tool-friendly APIs (Sessions 12)
- Every HTTP response includes `X-Trace-Id`.
- Health check: `GET /health`.
- Rate limit headers: `X-RateLimit-*` (development stub).

## Security baseline (Session 11)
- Hashed credentials stored in `users` table (`app.cli create-user`).
- JWT issued via `POST /auth/login`.
- Admin-only route: `GET /admin/metrics`.
- Report creation allowed for `admin` or `worker` roles.
- Rotation steps:
  1) Update `JWT_SECRET` in `compose.yaml` (or env).
  2) Restart API + worker.
  3) Re-issue tokens (login again).

## Enhancement
- Searchable series catalog: `GET /series?query=...` filters by title/creator.

## AI integration
- `POST /ai/summary` generates a catalog summary using local Ollama (`OLLAMA_BASE_URL`, `OLLAMA_MODEL`).
