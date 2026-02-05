# Compose Runbook

## Launch stack
```bash
docker compose up --build
```

## Pull Ollama model
```bash
docker compose exec ollama ollama pull llama3.1
```

## Create users
```bash
docker compose exec api python -m app.cli create-user --username admin --password admin-pass --role admin
docker compose exec api python -m app.cli create-user --username worker --password worker-pass --role worker
```

## Verify health + rate limit headers
```bash
curl -s http://localhost:8000/health
curl -i http://localhost:8000/series | rg -i "x-ratelimit|x-trace-id"
```

## Queue a report job
```bash
TOKEN=$(curl -s http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin-pass"}' | jq -r .access_token)

curl -s -X POST http://localhost:8000/reports/queue \
  -H "Authorization: Bearer ${TOKEN}"
```

## CI checks
```bash
uv run pytest
uv run schemathesis run http://localhost:8000/openapi.json
```
