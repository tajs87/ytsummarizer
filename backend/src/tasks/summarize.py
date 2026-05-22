"""
Celery task for generating AI summaries from video transcriptions.
Processes completed transcriptions and creates summary records.
"""

import asyncio

from sqlalchemy.orm import Session

from src.core.errors import TranscriptionFailedError, VideoNotFoundError
from src.db.session import SessionLocal
from src.models.summary import Summary, SummaryType
from src.models.transcription import Transcription
from src.models.video import Video
from src.services.summarization_service import summarization_service
from src.tasks.app import celery_app


@celery_app.task(name="tasks.generate_summary", bind=True, max_retries=2)
def generate_summary_task(
    self,
    video_id: int,
    summary_type: str = "brief",
) -> dict:
    """
    Generate summary for a transcribed video.

    Args:
        video_id: ID of the video
        summary_type: Type of summary to generate

    Returns:
        Dict with summary_id and video_id

    Raises:
        NotFoundError: If video or transcription not found
        TranscriptionFailedError: If summarization fails
    """
    db: Session = SessionLocal()

    try:
        # Get video
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise VideoNotFoundError(video_id)

        # Get transcription
        transcription = db.query(Transcription).filter(
            Transcription.video_id == video_id
        ).first()
        if not transcription:
            raise VideoNotFoundError(video_id)

        # Validate summary type
        try:
            summary_enum = SummaryType(summary_type)
        except ValueError:
            summary_enum = SummaryType.BRIEF

        # Generate summary using AI service
        summary_content = asyncio.run(
            summarization_service.generate_summary(
                transcription_text=transcription.full_text,
                summary_type=summary_type,
            )
        )

        # Create summary record
        summary = Summary(
            video_id=video_id,
            summary_type=summary_enum,
            content=summary_content,
        )
        db.add(summary)
        db.commit()
        db.refresh(summary)

        return {
            "summary_id": summary.id,
            "video_id": video_id,
            "summary_type": summary_type,
        }

    except Exception as e:
        db.rollback()
        raise TranscriptionFailedError(f"Summary generation failed: {str(e)}") from e

    finally:
        db.close()
