"""
Pytest configuration and shared fixtures for backend tests.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.session import Base
from src.models.user import User  # noqa: F401 - imported for table creation


@pytest.fixture(scope="function")
def test_db() -> Session:
    """
    Create a test database session with isolated transaction.
    
    Each test gets a fresh database with all tables created.
    Changes are rolled back after the test completes.
    
    Yields:
        Database session for testing
    """
    # Create in-memory SQLite database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(test_db: Session) -> User:
    """
    Create a test user for authentication tests.
    
    Args:
        test_db: Test database session
    
    Returns:
        User instance
    """
    from src.core.security import get_password_hash
    
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True,
        is_superuser=False,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    return user


@pytest.fixture
def test_superuser(test_db: Session) -> User:
    """
    Create a test superuser for admin tests.
    
    Args:
        test_db: Test database session
    
    Returns:
        Superuser instance
    """
    from src.core.security import get_password_hash
    
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword123"),
        is_active=True,
        is_superuser=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    return user
