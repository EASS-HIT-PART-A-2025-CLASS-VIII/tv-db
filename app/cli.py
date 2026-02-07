import typer

from sqlmodel import delete

from .db import create_db_and_tables, session_context
from .models import SeriesCreate, SeriesDB, UserDB
from .security import hash_password
from .services.helpers import find_duplicate_series
from .services.users import get_user_by_username

cli = typer.Typer(help="Utility commands for the TV Series Catalogue API")


def _load_seed_data() -> list[dict]:
    """Return a compact dataset for quick smoke testing."""
    return [
        {"title": "Breaking Bad", "creator": "Vince Gilligan", "year": 2008, "rating": 9.5},
        {"title": "The Crown", "creator": "Peter Morgan", "year": 2016, "rating": 8.6},
        {"title": "Stranger Things", "creator": "Duffer Brothers", "year": 2016, "rating": 8.7},
    ]


def _load_series_search_seed_data() -> list[dict]:
    """Return a TV series dataset for search demos."""
    return [
        {"title": "The Bear", "creator": "Christopher Storer", "year": 2022, "rating": 8.6},
        {"title": "Severance", "creator": "Dan Erickson", "year": 2022, "rating": 8.7},
        {"title": "Succession", "creator": "Jesse Armstrong", "year": 2018, "rating": 8.8},
        {"title": "Andor", "creator": "Tony Gilroy", "year": 2022, "rating": 8.4},
        {"title": "Silo", "creator": "Graham Yost", "year": 2023, "rating": 8.2},
        {"title": "The White Lotus", "creator": "Mike White", "year": 2021, "rating": 8.0},
    ]


def _load_full_seed_data() -> list[dict]:
    """Return a larger dataset for fuller demos."""
    return [
        {"title": "Breaking Bad", "creator": "Vince Gilligan", "year": 2008, "rating": 9.5},
        {"title": "Better Call Saul", "creator": "Vince Gilligan", "year": 2015, "rating": 8.9},
        {"title": "The Sopranos", "creator": "David Chase", "year": 1999, "rating": 9.2},
        {"title": "The Wire", "creator": "David Simon", "year": 2002, "rating": 9.3},
        {"title": "Mad Men", "creator": "Matthew Weiner", "year": 2007, "rating": 8.7},
        {"title": "Succession", "creator": "Jesse Armstrong", "year": 2018, "rating": 8.8},
        {"title": "The Bear", "creator": "Christopher Storer", "year": 2022, "rating": 8.6},
        {"title": "Severance", "creator": "Dan Erickson", "year": 2022, "rating": 8.7},
        {"title": "Andor", "creator": "Tony Gilroy", "year": 2022, "rating": 8.4},
        {"title": "Silo", "creator": "Graham Yost", "year": 2023, "rating": 8.2},
        {"title": "The White Lotus", "creator": "Mike White", "year": 2021, "rating": 8.0},
        {"title": "The Crown", "creator": "Peter Morgan", "year": 2016, "rating": 8.6},
        {"title": "Stranger Things", "creator": "Duffer Brothers", "year": 2016, "rating": 8.7},
        {"title": "Mr. Robot", "creator": "Sam Esmail", "year": 2015, "rating": 8.5},
        {"title": "Chernobyl", "creator": "Craig Mazin", "year": 2019, "rating": 9.3},
        {"title": "The Last of Us", "creator": "Craig Mazin", "year": 2023, "rating": 8.8},
        {"title": "True Detective", "creator": "Nic Pizzolatto", "year": 2014, "rating": 8.9},
        {"title": "Fargo", "creator": "Noah Hawley", "year": 2014, "rating": 8.9},
        {"title": "House of the Dragon", "creator": "Ryan Condal", "year": 2022, "rating": 8.4},
        {"title": "The Americans", "creator": "Joe Weisberg", "year": 2013, "rating": 8.4},
        {"title": "Peaky Blinders", "creator": "Steven Knight", "year": 2013, "rating": 8.8},
        {"title": "Black Mirror", "creator": "Charlie Brooker", "year": 2011, "rating": 8.7},
        {"title": "Dark", "creator": "Baran bo Odar", "year": 2017, "rating": 8.8},
        {"title": "Ozark", "creator": "Bill Dubuque", "year": 2017, "rating": 8.5},
        {"title": "Narcos", "creator": "Carlo Bernard", "year": 2015, "rating": 8.8},
    ]


@cli.command()
def init_db() -> None:
    """Create database tables."""
    create_db_and_tables()
    typer.echo("Database ready.")


@cli.command()
def seed(
    clear_existing: bool = typer.Option(True, help="Wipe existing series before seeding."),
) -> None:
    """Seed the database with a few sample TV series."""
    create_db_and_tables()

    with session_context() as session:
        if clear_existing:
            session.exec(delete(SeriesDB))
            session.commit()

        for data in _load_seed_data():
            series_payload = SeriesCreate(**data)
            if find_duplicate_series(series_payload, session):
                continue
            session.add(SeriesDB(**data))
        session.commit()

    typer.echo("Seed data inserted.")


@cli.command()
def seed_search(
    clear_existing: bool = typer.Option(False, help="Wipe existing series before seeding."),
) -> None:
    """Seed the database with TV series entries for search demos."""
    create_db_and_tables()

    with session_context() as session:
        if clear_existing:
            session.exec(delete(SeriesDB))
            session.commit()

        for data in _load_series_search_seed_data():
            series_payload = SeriesCreate(**data)
            if find_duplicate_series(series_payload, session):
                continue
            session.add(SeriesDB(**data))
        session.commit()

    typer.echo("Search seed data inserted.")


@cli.command()
def seed_full(
    clear_existing: bool = typer.Option(True, help="Wipe existing series before seeding."),
    admin_username: str = typer.Option("admin", help="Admin username to create if missing."),
    admin_password: str = typer.Option("admin-pass", help="Admin password to hash."),
    admin_role: str = typer.Option("admin", help="Role for the admin user."),
) -> None:
    """Seed the database with many series and ensure an admin user exists."""
    create_db_and_tables()

    with session_context() as session:
        if clear_existing:
            session.exec(delete(SeriesDB))
            session.commit()

        for data in _load_full_seed_data():
            series_payload = SeriesCreate(**data)
            if find_duplicate_series(series_payload, session):
                continue
            session.add(SeriesDB(**data))
        session.commit()

        if not get_user_by_username(session, admin_username):
            user = UserDB(
                username=admin_username,
                hashed_password=hash_password(admin_password),
                role=admin_role,
            )
            session.add(user)
            session.commit()
            typer.echo(f"Created user '{admin_username}' with role '{admin_role}'.")
        else:
            typer.echo(f"User '{admin_username}' already exists.")

    typer.echo("Full seed data inserted.")


@cli.command()
def create_user(
    username: str = typer.Option(..., help="Username for the new account."),
    password: str = typer.Option(..., help="Plaintext password to hash."),
    role: str = typer.Option("viewer", help="Role for the user."),
) -> None:
    """Create a hashed-credential user."""
    create_db_and_tables()
    with session_context() as session:
        if get_user_by_username(session, username):
            typer.echo(f"User '{username}' already exists.")
            raise typer.Exit(code=1)
        user = UserDB(username=username, hashed_password=hash_password(password), role=role)
        session.add(user)
        session.commit()
    typer.echo(f"Created user '{username}' with role '{role}'.")


if __name__ == "__main__":
    cli()
