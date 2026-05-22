"""
Authentication endpoints for user registration and login.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.core.errors import InvalidCredentialsError
from src.core.security import create_access_token, get_password_hash, verify_password
from src.db.session import get_db
from src.models.user import User
from src.schemas.auth import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from src.schemas.errors import ErrorResponse

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Email already registered"},
    },
)
def register(
    user_data: UserRegisterRequest,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """
    Register a new user account.
    
    - **email**: Valid email address (unique)
    - **password**: Minimum 8 characters
    
    Returns user profile on success.
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "AUTH-004",
                "message": "Email already registered",
                "details": {"email": user_data.email},
            },
        )
    
    # Create new user
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
    },
)
def login(
    credentials: UserLoginRequest,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    """
    Authenticate user and return JWT access token.
    
    - **email**: Registered email address
    - **password**: User password
    
    Returns JWT token for authenticated requests.
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    # Verify password
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise InvalidCredentialsError()
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error_code": "AUTH-005",
                "message": "User account is inactive",
                "details": {},
            },
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return TokenResponse(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get current authenticated user's profile.
    
    Requires valid JWT token in Authorization header.
    """
    return current_user
