FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir uv \
    && uv pip install --system -r pyproject.toml

COPY app/ ./app/
COPY scripts/start.sh ./scripts/start.sh
COPY streamlit_app.py ./

RUN chmod +x /app/scripts/start.sh

EXPOSE 8000
EXPOSE 8501

CMD ["/app/scripts/start.sh"]
