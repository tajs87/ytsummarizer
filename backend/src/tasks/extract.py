"""
Celery task for video extraction.
Downloads audio from video URL and prepares for transcription.
"""
import tempfile
from pathlib import Path

from celery import Task
from sqlalchemy.orm import Session

from src.core.errors import VideoExtractionError
from src.db.session import SessionLocal
from src.models.video import Video, VideoStatus
from src.services.cache_service import cache_service
from src.services.video_extractor import video_extractor
from src.tasks.app import celery_app
from src.tasks.base import ProgressTask


@celery_app.task(bind=True, base=ProgressTask, name="tasks.extract_video")
def extract_video_task(self: Task, video_id: int) -> dict[str, str]:
    """
    Extract audio and metadata from video URL.
    
    Args:
        video_id: Database ID of video to process
    
    Returns:
        Dictionary with audio_path and extracted metadata
    
    Workflow:
        1. Update video status to EXTRACTING
        2. Extract metadata (title, duration)
        3. Download audio file
        4. Cache metadata
        5. Return audio path for transcription task
    
    Raises:
        VideoExtractionError: If extraction fails
    """
    db: Session = SessionLocal()
    video: Video | None = None
    audio_path: Path | None = None
    
    try:
        # Fetch video from database
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise VideoExtractionError(
                message=f"Video {video_id} not found in database",
                details={"video_id": video_id},
            )
        
        # Update status to EXTRACTING
        video.status = VideoStatus.EXTRACTING
        db.commit()
        self.update_progress(10, "Starting video extraction...")
        
        # Extract metadata first
        self.update_progress(20, "Extracting video metadata...")
        metadata = video_extractor._extract_metadata_sync(video.url)
        
        # Update video with metadata
        video.title = metadata.get("title")
        video.duration_seconds = metadata.get("duration_seconds")
        db.commit()
        
        # Cache metadata
        cache_service_sync = cache_service  # Use sync methods in Celery
        cache_service._set_video_metadata_sync(video.url_hash, metadata)
        
        self.update_progress(40, "Downloading audio...")
        
        # Download audio to temp location
        temp_dir = Path(tempfile.mkdtemp())
        audio_path = video_extractor._download_audio_sync(
            video.url, temp_dir / f"video_{video_id}"
        )
        
        self.update_progress(80, "Audio extraction complete")
        
        # Return audio path for next task
        return {
            "audio_path": str(audio_path),
            "video_id": video_id,
            "duration_seconds": video.duration_seconds or 0,
        }
    
    except Exception as e:
        # Update video status to FAILED
        if video:
            video.status = VideoStatus.FAILED
            video.error_message = str(e)
            db.commit()
        
        # Clean up temp audio file
        if audio_path and audio_path.exists():
            audio_path.unlink()
        
        raise VideoExtractionError(
            message=f"Video extraction failed: {str(e)}",
            details={"video_id": video_id, "error": str(e)},
        )
    
    finally:
        db.close()


# Helper method for synchronous cache operations in Celery
def _set_video_metadata_sync(cache, url_hash: str, metadata: dict) -> None:
    """Synchronous cache set for Celery tasks."""
    import json
    import redis
    
    from src.core.config import get_settings
    from src.services.cache_service import CACHE_TTL_SECONDS
    
    settings = get_settings()
    
    # Create sync Redis client for Celery context
    sync_redis = redis.from_url(
        str(settings.redis_url),
        encoding="utf-8",
        decode_responses=True,
    )
    
    key = f"video_meta:{url_hash}"
    sync_redis.set(
        key,
        json.dumps(metadata),
        ex=CACHE_TTL_SECONDS,
    )


# Monkey-patch the sync method onto cache_service
cache_service._set_video_metadata_sync = lambda url_hash, metadata: _set_video_metadata_sync(
    cache_service, url_hash, metadata
)
