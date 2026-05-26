"""
FastAPI middleware for CORS and rate limiting.
"""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from fastapi import Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.config import get_settings
from src.core.security import decode_access_token
from src.db.session import SessionLocal
from src.models.user import User

settings = get_settings()


def configure_cors(app: object) -> None:
    """
    Configure CORS middleware for the application.

    Args:
        app: FastAPI application instance
    """
    app.add_middleware(  # type: ignore
        CORSMiddleware,
        allow_origins=settings.get_allowed_origins_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce per-user rate limits on video processing.

    Constitution requirement: 10 videos/hour per user (FR-010)
    Only applies to video submission endpoints.
    """

    def __init__(self, app: object):
        super().__init__(app)  # type: ignore
        self.rate_limit_paths = ["/api/v1/videos"]  # Paths that consume rate limit

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Response],  # type: ignore[override]
    ) -> Response:
        """Process request and enforce rate limits."""
        # Only check rate limits for video submission (POST to /videos)
        if request.method == "POST" and any(
            request.url.path.startswith(path) for path in self.rate_limit_paths
        ):
            # Extract user from token
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                payload = decode_access_token(token)

                if payload:
                    email = payload.get("sub")
                    if email:
                        # Check rate limit
                        db: Session = SessionLocal()
                        try:
                            user = db.query(User).filter(User.email == email).first()
                            if user:
                                # Reset counter if hour has passed
                                now = datetime.now(UTC)
                                if now >= user.rate_limit_reset_at:
                                    user.videos_processed_current_hour = 0
                                    user.rate_limit_reset_at = now + timedelta(hours=1)
                                    db.commit()

                                # Check if limit exceeded
                                if (
                                    user.videos_processed_current_hour
                                    >= settings.rate_limit_videos_per_hour
                                ):
                                    return JSONResponse(
                                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                                        content={
                                            "error_code": "RATE-001",
                                            "message": f"Rate limit exceeded. Maximum {settings.rate_limit_videos_per_hour} videos per hour.",
                                            "details": {
                                                "reset_at": user.rate_limit_reset_at.isoformat(),
                                                "current_count": user.videos_processed_current_hour,
                                                "limit": settings.rate_limit_videos_per_hour,
                                            },
                                        },
                                    )

                                # Increment counter
                                user.videos_processed_current_hour += 1
                                db.commit()
                        finally:
                            db.close()

        # Proceed with request
        response: Response = await call_next(request)  # type: ignore[misc]
        return response
