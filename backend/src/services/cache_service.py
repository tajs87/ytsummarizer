"""
Redis cache service for transcription results.
Implements 7-day TTL per plan.md caching strategy.
"""
import json
from typing import Any

import redis.asyncio as aioredis

from src.core.config import get_settings

settings = get_settings()

# Create Redis client
redis_client = aioredis.from_url(
    str(settings.redis_url),
    encoding="utf-8",
    decode_responses=True,
)

# Cache TTL: 7 days (per plan.md)
CACHE_TTL_SECONDS = 7 * 24 * 60 * 60  # 7 days


class CacheService:
    """
    Redis cache service for storing transcription results.

    Uses video URL hash as cache key for deduplication.
    """

    def __init__(self, client: aioredis.Redis = redis_client):  # type: ignore
        self.client = client

    async def get_transcription(self, url_hash: str) -> dict[str, Any] | None:
        """
        Retrieve cached transcription by URL hash.

        Args:
            url_hash: SHA256 hash of video URL

        Returns:
            Cached transcription data or None if not found

        Example:
            >>> cache = CacheService()
            >>> data = await cache.get_transcription("abc123...")
            >>> if data:
            ...     print(data["full_text"])
        """
        key = f"transcription:{url_hash}"
        cached_data = await self.client.get(key)

        if cached_data:
            return json.loads(cached_data)
        return None

    async def set_transcription(
        self, url_hash: str, transcription_data: dict[str, Any]
    ) -> None:
        """
        Cache transcription data with 7-day TTL.

        Args:
            url_hash: SHA256 hash of video URL
            transcription_data: Transcription data to cache

        Example:
            >>> cache = CacheService()
            >>> await cache.set_transcription("abc123...", {
            ...     "full_text": "Welcome to...",
            ...     "segments": [...]
            ... })
        """
        key = f"transcription:{url_hash}"
        await self.client.set(
            key,
            json.dumps(transcription_data),
            ex=CACHE_TTL_SECONDS,
        )

    async def invalidate_transcription(self, url_hash: str) -> None:
        """
        Remove cached transcription.

        Args:
            url_hash: SHA256 hash of video URL to invalidate
        """
        key = f"transcription:{url_hash}"
        await self.client.delete(key)

    async def get_video_metadata(self, url_hash: str) -> dict[str, Any] | None:
        """
        Retrieve cached video metadata.

        Args:
            url_hash: SHA256 hash of video URL

        Returns:
            Cached metadata or None
        """
        key = f"video_meta:{url_hash}"
        cached_data = await self.client.get(key)

        if cached_data:
            return json.loads(cached_data)
        return None

    async def set_video_metadata(
        self, url_hash: str, metadata: dict[str, Any]
    ) -> None:
        """
        Cache video metadata (title, duration, etc.).

        Args:
            url_hash: SHA256 hash of video URL
            metadata: Video metadata to cache
        """
        key = f"video_meta:{url_hash}"
        await self.client.set(
            key,
            json.dumps(metadata),
            ex=CACHE_TTL_SECONDS,
        )

    async def close(self) -> None:
        """Close Redis connection."""
        await self.client.close()


# Global cache service instance
cache_service = CacheService()
