"""
Celery task for extracting key highlights from summaries and transcriptions.
Identifies important segments with timestamps for quick navigation.
"""

import asyncio
from sqlalchemy.orm import Session

from src.db.session import SessionLocal
from src.models.summary import Summary
from src.models.transcription import Transcription
from src.models.highlight import Highlight
from src.core.errors import SummaryNotFoundError, VideoNotFoundError
from src.services.summarization_service import summarization_service
from src.tasks.app import celery_app


@celery_app.task(name="tasks.extract_highlights", bind=True, max_retries=2)
def extract_highlights_task(
    self,
    summary_ref: dict | int,
    max_highlights: int = 5,
) -> dict:
    """
    Extract highlights for a summary.

    Args:
        summary_ref: Summary ID or payload from generate_summary_task
        max_highlights: Maximum number of highlights

    Returns:
        Dict with summary_id and highlight count

    Raises:
        NotFoundError: If summary or transcription not found
    """
    db: Session = SessionLocal()

    if isinstance(summary_ref, dict):
        summary_id = int(summary_ref.get("summary_id", 0))
    else:
        summary_id = int(summary_ref)

    if summary_id <= 0:
        db.close()
        raise SummaryNotFoundError(summary_id)

    try:
        # Get summary
        summary = db.query(Summary).filter(Summary.id == summary_id).first()
        if not summary:
            raise SummaryNotFoundError(summary_id)

        # Get transcription for context
        transcription = db.query(Transcription).filter(
            Transcription.video_id == summary.video_id
        ).first()
        if not transcription:
            raise VideoNotFoundError(summary.video_id)

        # Extract highlights using AI service
        extracted_highlights = asyncio.run(
            summarization_service.extract_highlights(
                transcription_text=transcription.full_text,
                max_highlights=max_highlights,
            )
        )

        # Clear existing highlights for this summary
        db.query(Highlight).filter(Highlight.summary_id == summary_id).delete()

        # Create new highlights
        created_count = 0
        for idx, highlight_data in enumerate(extracted_highlights):
            # Map highlights to rough timestamp ranges
            # In production, would use semantic matching against segments
            segment_count = len(transcription.segments) if transcription.segments else 1
            segment_idx = min(idx * segment_count // max_highlights, segment_count - 1)

            if transcription.segments and segment_idx < len(transcription.segments):
                segment = transcription.segments[segment_idx]
                start_time = float(segment.get("start", 0))
                end_time = float(segment.get("end", start_time + 10))
            else:
                start_time = idx * 30.0
                end_time = start_time + 10.0

            highlight = Highlight(
                summary_id=summary_id,
                text=highlight_data.get("text", ""),
                start_time=start_time,
                end_time=end_time,
                importance_score=highlight_data.get("importance_score", 0.5),
            )
            db.add(highlight)
            created_count += 1

        db.commit()

        return {
            "summary_id": summary_id,
            "video_id": summary.video_id,
            "highlights_created": created_count,
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
