FROM python:3.11-slim

WORKDIR /app

ENV API_PORT=8000
ENV STREAMLIT_PORT=8501
ENV TV_API_BASE=http://localhost:${API_PORT}

COPY pyproject.toml ./
RUN pip install --no-cache-dir \
    fastapi==0.122.0 \
    requests==2.32.5 \
    sqlmodel==0.0.27 \
    streamlit==1.52.2 \
    uvicorn==0.38.0 \
    typer==0.20.0

COPY app/ ./app/
COPY streamlit_app.py ./

EXPOSE 8000
EXPOSE 8501

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${API_PORT} & streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port ${STREAMLIT_PORT}"]
