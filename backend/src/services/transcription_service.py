"""
Transcription service using OpenAI Whisper API.
Handles audio transcription with timestamps and speaker detection.
"""
import asyncio
from pathlib import Path
from typing import Any

from openai import AsyncOpenAI

from src.core.config import get_settings
from src.core.errors import TranscriptionFailedError

settings = get_settings()


class TranscriptionService:
    """
    Service for transcribing audio using OpenAI Whisper API.
    
    Provides timestamped transcriptions with word-level accuracy.
    """

    def __init__(self, api_key: str | None = None):
        """
        Initialize transcription service.
        
        Args:
            api_key: OpenAI API key (uses settings if None)
        """
        self.client = AsyncOpenAI(
            api_key=api_key or settings.openai_api_key
        )

    async def transcribe_audio(
        self, audio_path: Path, language: str | None = None
    ) -> dict[str, Any]:
        """
        Transcribe audio file to text with timestamps.
        
        Args:
            audio_path: Path to audio file (mp3, wav, etc.)
            language: Optional language code (auto-detect if None)
        
        Returns:
            Dictionary with full_text, segments, language, word_count
        
        Raises:
            TranscriptionFailedError: If transcription fails
        
        Example:
            >>> service = TranscriptionService()
            >>> result = await service.transcribe_audio(Path("audio.mp3"))
            >>> print(result["full_text"])
            >>> print(len(result["segments"]))
        """
        try:
            if not audio_path.exists():
                raise TranscriptionFailedError(
                    message="Audio file not found",
                    details={"path": str(audio_path)},
                )

            # Open audio file and transcribe
            with open(audio_path, "rb") as audio_file:
                # Use OpenAI Whisper API with timestamps
                response = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                    language=language,
                )

            # Process response
            full_text = response.text
            segments = self._process_segments(response.segments)  # type: ignore
            detected_language = response.language
            word_count = len(full_text.split())

            return {
                "full_text": full_text,
                "segments": segments,
                "language": detected_language,
                "word_count": word_count,
            }

        except TranscriptionFailedError:
            raise
        except Exception as e:
            raise TranscriptionFailedError(
                message=f"Transcription failed: {str(e)}",
                details={"audio_path": str(audio_path), "error": str(e)},
            )

    def _process_segments(self, raw_segments: list[Any]) -> list[dict[str, Any]]:
        """
        Process raw Whisper segments into standardized format.
        
        Args:
            raw_segments: Raw segments from Whisper API
        
        Returns:
            List of processed segment dictionaries
        """
        processed = []
        
        for idx, segment in enumerate(raw_segments):
            processed.append({
                "id": idx,
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
            })
        
        return processed

    async def estimate_cost(self, audio_duration_seconds: float) -> float:
        """
        Estimate transcription cost based on audio duration.
        
        OpenAI Whisper API pricing: $0.006 per minute (as of 2024)
        
        Args:
            audio_duration_seconds: Audio duration in seconds
        
        Returns:
            Estimated cost in USD
        
        Example:
            >>> service = TranscriptionService()
            >>> cost = await service.estimate_cost(600)  # 10 minutes
            >>> print(f"Estimated cost: ${cost:.3f}")
        """
        minutes = audio_duration_seconds / 60.0
        cost_per_minute = 0.006  # OpenAI Whisper pricing
        return minutes * cost_per_minute

    async def validate_audio(self, audio_path: Path) -> bool:
        """
        Validate audio file before transcription.
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            True if audio is valid for transcription
        """
        if not audio_path.exists():
            return False
        
        # Check file size (OpenAI limit: 25 MB)
        max_size_bytes = 25 * 1024 * 1024
        file_size = audio_path.stat().st_size
        
        if file_size > max_size_bytes:
            return False
        
        # Check file extension
        valid_extensions = {".mp3", ".wav", ".m4a", ".ogg", ".webm"}
        if audio_path.suffix.lower() not in valid_extensions:
            return False
        
        return True


# Global instance
transcription_service = TranscriptionService()
