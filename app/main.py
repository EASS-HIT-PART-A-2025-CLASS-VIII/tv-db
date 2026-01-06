import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import create_db_and_tables
from .routes.series import router as series_router

logger = logging.getLogger("tv_db")
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize application resources on startup."""
    # Initialize database tables at startup using lifespan to avoid deprecated events.
    create_db_and_tables()
    logger.info("API startup complete.")
    yield


app = FastAPI(title="TV Series Catalogue API", version="0.1.0", lifespan=lifespan)
cors_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Lightweight health check endpoint."""
    return {"status": "ok"}


app.include_router(series_router, prefix="/series", tags=["series"])
