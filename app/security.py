from datetime import datetime, timedelta, timezone
import re

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from pydantic import BaseModel

from .config import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, JWT_SECRET

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)


class TokenPayload(BaseModel):
    sub: str
    role: str
    exp: datetime


def hash_password(password: str) -> str:
    """Hash a plaintext password for storage."""
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored hash."""
    return pwd_context.verify(password, hashed_password)


def create_access_token(subject: str, role: str, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT for the given subject and role."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": subject, "role": role, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def password_strength_issues(password: str) -> list[str]:
    """Return a list of unmet password requirements."""
    issues: list[str] = []
    if len(password) < 8:
        issues.append("Password must be at least 8 characters long.")
    if not re.search(r"[a-z]", password):
        issues.append("Password must include a lowercase letter.")
    if not re.search(r"[A-Z]", password):
        issues.append("Password must include an uppercase letter.")
    if not re.search(r"\d", password):
        issues.append("Password must include a number.")
    if not re.search(r"[^\w\s]", password):
        issues.append("Password must include a symbol.")
    return issues


def _decode_token(token: str) -> TokenPayload:
    """Decode and validate a JWT token payload."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from exc
    return TokenPayload.model_validate(payload)


def get_current_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> TokenPayload:
    """Dependency for extracting and validating a bearer token."""
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return _decode_token(credentials.credentials)


def require_role(*roles: str):
    """Dependency factory enforcing that the token includes one of the required roles."""

    def _role_guard(payload: TokenPayload = Depends(get_current_token)) -> TokenPayload:
        if payload.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient privileges",
            )
        return payload

    return _role_guard
