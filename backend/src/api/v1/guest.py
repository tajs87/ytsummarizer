"""Guest session endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from src.core.config import get_settings
from src.db.session import get_db
from src.services.guest_session_service import guest_session_service

router = APIRouter(prefix="/guest", tags=["guest"])
settings = get_settings()


@router.post("/session")
def bootstrap_guest_session(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Create or refresh an anonymous guest session cookie."""
    existing_token = request.cookies.get(settings.guest_session_cookie_name)
    result = guest_session_service.bootstrap(db, existing_token)

    response.set_cookie(
        key=settings.guest_session_cookie_name,
        value=result.token,
        max_age=settings.guest_session_max_age_seconds,
        httponly=True,
        secure=settings.guest_session_secure_cookie,
        samesite=settings.guest_session_same_site,
        path="/",
    )
    return {"session_state": "active"}
