from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db import create_db_and_tables
from .routes.series import router as series_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Initialize database tables at startup using lifespan to avoid deprecated events.
    create_db_and_tables()
    yield


app = FastAPI(title="TV Series Catalogue API", version="0.1.0", lifespan=lifespan)
app.include_router(series_router, prefix="/series", tags=["series"])
