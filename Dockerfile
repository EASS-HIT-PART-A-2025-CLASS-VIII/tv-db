FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir \
    fastapi==0.122.0 \
    requests==2.32.5 \
    sqlmodel==0.0.27 \
    streamlit==1.52.2 \
    uvicorn==0.38.0 \
    typer==0.20.0

COPY app/ ./app/
COPY scripts/start.sh ./scripts/start.sh
COPY streamlit_app.py ./

RUN chmod +x /app/scripts/start.sh

EXPOSE 8000
EXPOSE 8501

CMD ["/app/scripts/start.sh"]
