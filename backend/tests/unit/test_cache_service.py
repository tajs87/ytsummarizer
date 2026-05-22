import pytest

from src.services.cache_service import CacheService


class FakeRedis:
    def __init__(self):
        self.data = {}

    async def get(self, key):
        return self.data.get(key)

    async def set(self, key, value, ex=None):
        self.data[key] = value

    async def delete(self, key):
        self.data.pop(key, None)

    async def close(self):
        return None


@pytest.mark.asyncio
async def test_cache_service_set_get_invalidate_transcription():
    redis = FakeRedis()
    cache = CacheService(client=redis)

    payload = {"full_text": "hello", "segments": []}
    await cache.set_transcription("hash-1", payload)

    loaded = await cache.get_transcription("hash-1")
    assert loaded == payload

    await cache.invalidate_transcription("hash-1")
    assert await cache.get_transcription("hash-1") is None


@pytest.mark.asyncio
async def test_cache_service_metadata_round_trip():
    redis = FakeRedis()
    cache = CacheService(client=redis)

    meta = {"title": "test", "duration_seconds": 10}
    await cache.set_video_metadata("hash-2", meta)

    loaded = await cache.get_video_metadata("hash-2")
    assert loaded == meta
