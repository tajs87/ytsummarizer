"""
Test database utilities and helpers.
"""
from typing import Any

from sqlalchemy.orm import Session

from src.core.security import get_password_hash
from src.models.user import User


def create_test_user(
    db: Session,
    email: str = "testuser@example.com",
    password: str = "testpassword",
    **kwargs: Any,
) -> User:
    """
    Create a test user with given parameters.
    
    Args:
        db: Database session
        email: User email
        password: Plain text password
        **kwargs: Additional user fields
    
    Returns:
        Created user instance
    """
    user_data = {
        "email": email,
        "hashed_password": get_password_hash(password),
        "is_active": True,
        "is_superuser": False,
    }
    user_data.update(kwargs)
    
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


def get_test_token(user_email: str) -> str:
    """
    Generate a test JWT token for a user.
    
    Args:
        user_email: Email of user to generate token for
    
    Returns:
        JWT token string
    """
    from src.core.security import create_access_token
    
    return create_access_token(data={"sub": user_email})
