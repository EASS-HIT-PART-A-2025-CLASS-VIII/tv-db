import typer

from sqlmodel import delete

from .db import create_db_and_tables, session_context
from .models import SeriesDB

cli = typer.Typer(help="Utility commands for the TV Series Catalogue API")


def _load_seed_data() -> list[dict]:
    # Compact sample dataset for quick smoke testing
    return [
        {"title": "Breaking Bad", "creator": "Vince Gilligan", "year": 2008, "rating": 9.5},
        {"title": "The Crown", "creator": "Peter Morgan", "year": 2016, "rating": 8.6},
        {"title": "Stranger Things", "creator": "Duffer Brothers", "year": 2016, "rating": 8.7},
    ]


@cli.command()
def init_db() -> None:
    create_db_and_tables()
    typer.echo("Database ready.")


@cli.command()
def seed(clear_existing: bool = typer.Option(True, help="Wipe existing series before seeding.")) -> None:
    """Seed the database with a few sample TV series."""
    create_db_and_tables()

    with session_context() as session:
        if clear_existing:
            session.exec(delete(SeriesDB))
            session.commit()

        for data in _load_seed_data():
            session.add(SeriesDB(**data))
        session.commit()

    typer.echo("Seed data inserted.")


if __name__ == "__main__":
    cli()
