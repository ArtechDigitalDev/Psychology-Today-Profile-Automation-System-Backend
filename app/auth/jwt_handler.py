"""
jwt_handler.py
JWT token creation and verification for user authentication.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from app.config import settings
from app.schemas.auth import TokenData


def create_access_token(data: dict, expires_delta: int = None):
    """Create a new JWT access token. expires_delta is in days."""
    to_encode = data.copy()
    print("expires_delta", expires_delta)
    if expires_delta:
        expire = datetime.now(timezone.utc) + timedelta(days=expires_delta)
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = TokenData(username=username)
        return token_data
    except JWTError:
        return None 