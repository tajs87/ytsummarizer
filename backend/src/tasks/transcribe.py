"""
Celery task for audio transcription.
Uses OpenAI Whisper to transcribe audio and store results.
"""
import asyncio
from datetime import datetime
from pathlib import Path

from celery import Task
from sqlalchemy.orm import Session

from src.core.errors import TranscriptionFailedError
from src.db.session import SessionLocal
from src.models.transcription import Transcription
from src.models.video import Video, VideoStatus
from src.services.cache_service import cache_service
from src.services.transcription_service import transcription_service
from src.tasks.app import celery_app
from src.tasks.base import ProgressTask


@celery_app.task(bind=True, base=ProgressTask, name="tasks.transcribe_audio")
def transcribe_audio_task(
    self: Task, extract_result: dict, video_id: int
) -> dict[str, int]:
    """
    Transcribe audio file and save results to database.
    
    Args:
        extract_result: Result dict from extract_video_task containing:
            - audio_path: Path to audio file
            - video_id: Database ID of video
            - duration_seconds: Video duration
        video_id: Database ID of video (passed from chain)
    
    Returns:
        Dictionary with transcription_id
    
    Workflow:
        1. Update video status to TRANSCRIBING
        2. Transcribe audio using OpenAI Whisper
        3. Create Transcription record in database
        4. Cache transcription result
        5. Update video status to COMPLETED
        6. Clean up temp audio file
    
    Raises:
        TranscriptionFailedError: If transcription fails
    """
    # Unpack extract result
    audio_path = extract_result["audio_path"]
    duration_seconds = extract_result.get("duration_seconds", 0)
    
    db: Session = SessionLocal()
    video: Video | None = None
    audio_file = Path(audio_path)
    
    try:
        # Fetch video from database
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise TranscriptionFailedError(
                message=f"Video {video_id} not found in database",
                details={"video_id": video_id},
            )
        
        # Update status to TRANSCRIBING
        video.status = VideoStatus.TRANSCRIBING
        db.commit()
        self.update_progress(10, "Starting transcription...")
        
        # Validate audio file
        if not audio_file.exists():
            raise TranscriptionFailedError(
                message="Audio file not found",
                details={"audio_path": audio_path},
            )
        
        self.update_progress(20, "Transcribing audio with OpenAI Whisper...")
        
        # Transcribe audio (run async function in sync context)
        start_time = datetime.now()
        transcription_result = asyncio.run(
            transcription_service.transcribe_audio(audio_file)
        )
        processing_time = (datetime.now() - start_time).total_seconds()
        
        self.update_progress(70, "Saving transcription...")
        
        # Create Transcription record
        transcription = Transcription(
            video_id=video_id,
            full_text=transcription_result["full_text"],
            segments=transcription_result["segments"],
            language=transcription_result["language"],
            word_count=transcription_result["word_count"],
            processing_time_seconds=processing_time,
        )
        db.add(transcription)
        
        # Update video status to COMPLETED
        video.status = VideoStatus.COMPLETED
        video.completed_at = datetime.now()
        db.commit()
        
        self.update_progress(90, "Caching transcription...")
        
        # Cache transcription result
        _cache_transcription_sync(
            cache_service,
            video.url_hash,
            {
                "full_text": transcription.full_text,
                "segments": transcription.segments,
                "language": transcription.language,
                "word_count": transcription.word_count,
            },
        )
        
        self.update_progress(100, "Transcription complete!")
        
        return {
            "transcription_id": transcription.id,
            "video_id": video_id,
            "word_count": transcription.word_count,
        }
    
    except Exception as e:
        # Update video status to FAILED
        if video:
            video.status = VideoStatus.FAILED
            video.error_message = str(e)
            db.commit()
        
        raise TranscriptionFailedError(
            message=f"Transcription failed: {str(e)}",
            details={"video_id": video_id, "error": str(e)},
        )
    
    finally:
        # Clean up temp audio file
        if audio_file.exists():
            audio_file.unlink()
        
        # Clean up temp directory if empty
        if audio_file.parent.exists() and not list(audio_file.parent.iterdir()):
            audio_file.parent.rmdir()
        
        db.close()


def _cache_transcription_sync(cache, url_hash: str, data: dict) -> None:
    """Synchronous cache operation for Celery."""
    import json
    from src.services.cache_service import CACHE_TTL_SECONDS
    
    key = f"transcription:{url_hash}"
    # Use sync Redis in Celery context
    cache.client._redis.set(
        key,
        json.dumps(data),
        ex=CACHE_TTL_SECONDS,
    )
