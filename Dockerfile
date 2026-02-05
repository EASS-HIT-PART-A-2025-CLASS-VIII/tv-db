FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv \
    && uv venv /app/.venv \
    && uv sync --frozen --no-dev

COPY app/ ./app/
COPY scripts/start.sh ./scripts/start.sh
COPY streamlit_app.py ./

RUN chmod +x /app/scripts/start.sh

EXPOSE 8000
EXPOSE 8501

ENV PATH="/app/.venv/bin:$PATH"

CMD ["/app/scripts/start.sh"]
