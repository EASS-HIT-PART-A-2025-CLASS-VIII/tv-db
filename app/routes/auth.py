from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ..config import ACCESS_TOKEN_EXPIRE_MINUTES
from ..db import get_session
from ..models import LoginRequest, RegisterRequest, Token
from ..security import create_access_token, hash_password, verify_password
from ..services.users import create_viewer, get_user_by_username

router = APIRouter()


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(payload: LoginRequest, session: Session = Depends(get_session)) -> Token:
    """Exchange username/password for a JWT token."""
    user = get_user_by_username(session, payload.username)
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=user.username, role=user.role)
    return Token(
        access_token=token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, session: Session = Depends(get_session)) -> dict[str, str]:
    """Register a new viewer account."""
    create_viewer(session, payload.username, hash_password(payload.password))
    return {"status": "created"}
