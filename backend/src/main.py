"""
Main FastAPI application entry point.
Configures middleware, routes, and error handlers.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.middleware import RateLimitMiddleware
from src.api.v1 import auth, guest
from src.core.config import get_settings
from src.core.errors import YTSumError

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="YTSum API",
    description="Video Transcription & Summarization Service",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Include API routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(guest.router, prefix="/api/v1")

# Video and transcription routers
from src.api.v1 import shares, summaries, transcriptions, videos, ws  # noqa: E402

app.include_router(videos.router, prefix="/api/v1")
app.include_router(transcriptions.router, prefix="/api/v1")
app.include_router(summaries.router, prefix="/api/v1")
app.include_router(shares.router, prefix="/api/v1")
app.include_router(ws.router, prefix="/api/v1")


# Global exception handler for custom errors
@app.exception_handler(YTSumError)
async def ytsum_error_handler(request: Request, exc: YTSumError) -> JSONResponse:
    """
    Handle custom YTSum exceptions with structured error responses.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
        },
    )


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """
    Health check endpoint for monitoring.
    """
    return {"status": "healthy", "service": "ytsum-backend"}


# Root endpoint
@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """
    Root endpoint with API information.
    """
    return {
        "name": "YTSum API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
