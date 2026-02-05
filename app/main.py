import logging
import os
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import RATE_LIMIT_LIMIT, RATE_LIMIT_WINDOW_SECONDS
from .db import create_db_and_tables
from .routes.admin import router as admin_router
from .routes.ai import router as ai_router
from .routes.auth import router as auth_router
from .routes.reports import router as reports_router
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


@app.middleware("http")
async def trace_id_header(request, call_next):
    trace_id = request.headers.get("X-Trace-Id") or str(uuid.uuid4())
    request.state.trace_id = trace_id
    response = await call_next(request)
    response.headers["X-Trace-Id"] = trace_id
    return response


@app.middleware("http")
async def rate_limit_headers(request, call_next):
    response = await call_next(request)
    reset_epoch = int(time.time()) + RATE_LIMIT_WINDOW_SECONDS
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(max(RATE_LIMIT_LIMIT - 1, 0))
    response.headers["X-RateLimit-Reset"] = str(reset_epoch)
    return response


@app.get("/health")
def health_check() -> dict[str, str]:
    """Lightweight health check endpoint."""
    return {"status": "ok"}


app.include_router(series_router, prefix="/series", tags=["series"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(reports_router, prefix="/reports", tags=["reports"])
app.include_router(auth_router, prefix="/api", tags=["auth"])
app.include_router(admin_router, prefix="/api", tags=["admin"])
app.include_router(ai_router, prefix="/ai", tags=["ai"])
app.include_router(ai_router, prefix="/api/ai", tags=["ai"])
