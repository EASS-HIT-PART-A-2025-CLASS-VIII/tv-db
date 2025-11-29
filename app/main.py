from typing import Any, Dict, List
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import Session, select

from .db import create_db_and_tables, get_session
from .models import Movie, MovieCreate, Series, SeriesCreate


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Use lifespan instead of pon_event startup since it gave depcrecated warnings.
    create_db_and_tables()
    yield


app = FastAPI(title="TV Series Catalogue API", version="0.1.0", lifespan=lifespan)


def _model_dump(model: Any, *, exclude_unset: bool = False) -> Dict[str, Any]:
    """Compatibility helper for Pydantic v1/v2 model dump."""
    if hasattr(model, "model_dump"):
        return model.model_dump(exclude_unset=exclude_unset)
    return model.dict(exclude_unset=exclude_unset)

@app.get("/series", response_model=List[Series])
def list_series(session: Session = Depends(get_session)) -> List[Series]:
    series_list = session.exec(select(Series)).all()
    return series_list


@app.post("/series", response_model=Series, status_code=status.HTTP_201_CREATED)
def create_series(series: SeriesCreate, session: Session = Depends(get_session)) -> Series:
    db_series = Series(**_model_dump(series))
    session.add(db_series)
    session.commit()
    session.refresh(db_series)
    return db_series


@app.get("/series/{series_id}", response_model=Series)
def get_series(series_id: int, session: Session = Depends(get_session)) -> Series:
    series = session.get(Series, series_id)
    if series is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Series not found")
    return series
@app.delete("/series/{series_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_series(series_id: int, session: Session = Depends(get_session)) -> None:
    series = session.get(Series, series_id)
    if series is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Series not found")

    session.delete(series)
    session.commit()
    return None


@app.get("/movies", response_model=List[Movie])
def list_movies(session: Session = Depends(get_session)) -> List[Movie]:
    movies = session.exec(select(Movie)).all()
    return movies


@app.post("/movies", response_model=Movie, status_code=status.HTTP_201_CREATED)
def create_movie(movie: MovieCreate, session: Session = Depends(get_session)) -> Movie:
    db_movie = Movie(**_model_dump(movie))
    session.add(db_movie)
    session.commit()
    session.refresh(db_movie)
    return db_movie


@app.get("/movies/{movie_id}", response_model=Movie)
def get_movie(movie_id: int, session: Session = Depends(get_session)) -> Movie:
    movie = session.get(Movie, movie_id)
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return movie
