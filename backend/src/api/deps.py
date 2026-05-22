"""FastAPI dependencies for authentication, guest context, and database access."""
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.core.config import get_settings
from src.core.security import decode_access_token
from src.db.session import get_db
from src.models.guest_session import GuestSession
from src.models.user import User
from src.services.guest_session_service import guest_session_service

security = HTTPBearer(auto_error=False)
settings = get_settings()


@dataclass
class RequestContext:
    """Resolved ownership context for endpoints that allow guest and auth access."""

    user: User | None = None
    guest_session: GuestSession | None = None

    @property
    def is_authenticated(self) -> bool:
        return self.user is not None

    @property
    def is_guest(self) -> bool:
        return self.guest_session is not None and self.user is None


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Database session
    
    Returns:
        Authenticated User model instance
    
    Raises:
        HTTPException: 401 if token is invalid or user not found
    
    Example:
        @app.get("/me")
        def get_me(current_user: User = Depends(get_current_user)):
            return current_user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if credentials is None:
        raise credentials_exception

    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise credentials_exception
    
    email: str | None = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Dependency to ensure user is active.
    
    This is a convenience wrapper around get_current_user that explicitly
    checks the is_active flag (though get_current_user already does this).
    """
    return current_user


async def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Dependency to ensure user is a superuser.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User if they are a superuser
    
    Raises:
        HTTPException: 403 if user is not a superuser
    
    Example:
        @app.delete("/users/{user_id}")
        def delete_user(
            user_id: int,
            _: User = Depends(get_current_superuser)
        ):
            # Only superusers can delete users
            pass
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


async def get_request_context(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[Session, Depends(get_db)],
) -> RequestContext:
    """Resolve authenticated user context, or fallback to active guest session."""
    if credentials is not None:
        payload = decode_access_token(credentials.credentials)
        if payload and isinstance(payload.get("sub"), str):
            email = payload["sub"]
            user = db.query(User).filter(User.email == email).first()
            if user and user.is_active:
                return RequestContext(user=user)

    guest_token = request.cookies.get(settings.guest_session_cookie_name)
    if guest_token:
        guest_session = guest_session_service.get_active_session(db, guest_token)
        if guest_session:
            guest_session_service.touch_session(db, guest_session)
            return RequestContext(guest_session=guest_session)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No valid auth or guest session context",
        headers={"WWW-Authenticate": "Bearer"},
    )
