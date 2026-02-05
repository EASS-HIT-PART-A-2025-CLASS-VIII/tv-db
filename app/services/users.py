from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..models import UserDB


def get_user_by_username(session: Session, username: str) -> UserDB | None:
    """Return a user record by username."""
    return session.exec(select(UserDB).where(UserDB.username == username)).first()


def require_user(session: Session, username: str) -> UserDB:
    """Return a user or raise a 404."""
    user = get_user_by_username(session, username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def create_viewer(session: Session, username: str, hashed_password: str) -> UserDB:
    """Create a viewer user if it does not exist."""
    if get_user_by_username(session, username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    user = UserDB(username=username, hashed_password=hashed_password, role="viewer")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
