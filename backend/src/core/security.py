"""
Security utilities for authentication and authorization.
Implements JWT token generation and password hashing.
"""

from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.core.config import get_settings

settings = get_settings()

# Password hashing context.
# `bcrypt` has runtime compatibility issues with some recent bcrypt wheels in this stack,
# so use a stable passlib-native scheme for local/dev reliability.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password from database

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password for storage.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload data to encode in token (typically {"sub": user_id})
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string

    Example:
        >>> token = create_access_token({"sub": "user@example.com"})
        >>> # Token valid for settings.access_token_expire_minutes
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    Decode and validate a JWT access token.

    Args:
        token: JWT token string to decode

    Returns:
        Decoded token payload if valid, None otherwise

    Example:
        >>> payload = decode_access_token(token)
        >>> if payload:
        ...     user_id = payload.get("sub")
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None
