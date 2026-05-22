"""
Video extraction service using yt-dlp.
Handles downloading audio and extracting metadata from video URLs.
"""

import asyncio
import tempfile
from pathlib import Path
from typing import Any

import yt_dlp

from src.core.errors import VideoExtractionError
from src.models.video import VideoPlatform
from src.services.platform_detector import platform_detector
from src.utils.validators import validate_platform_url


class VideoExtractor:
    """
    Service for extracting audio and metadata from video URLs.

    Supports YouTube, Vimeo, and direct video links via yt-dlp.
    """

    def __init__(self) -> None:
        """Initialize video extractor with default options."""
        self.ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "nocheckcertificate": True,
        }

    async def extract_metadata(self, url: str) -> dict[str, Any]:
        """
        Extract video metadata without downloading.

        Args:
            url: Video URL to extract metadata from

        Returns:
            Dictionary with title, duration, platform, etc.

        Raises:
            VideoExtractionError: If metadata extraction fails

        Example:
            >>> extractor = VideoExtractor()
            >>> metadata = await extractor.extract_metadata("https://youtube.com/...")
            >>> print(metadata["title"])
        """
        try:
            loop = asyncio.get_event_loop()
            metadata = await loop.run_in_executor(None, self._extract_metadata_sync, url)
            return metadata
        except Exception as e:
            raise VideoExtractionError(
                message=f"Failed to extract video metadata: {str(e)}",
                details={"url": url, "error": str(e)},
            ) from e

    def _extract_metadata_sync(self, url: str) -> dict[str, Any]:
        """Synchronous metadata extraction (runs in executor)."""
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Determine platform from URL
            platform = self._detect_platform(url, info)

            return {
                "title": info.get("title", "Unknown"),
                "duration_seconds": info.get("duration"),
                "platform": platform,
                "thumbnail_url": info.get("thumbnail"),
                "uploader": info.get("uploader"),
                "upload_date": info.get("upload_date"),
            }

    async def download_audio(self, url: str, output_path: Path | None = None) -> Path:
        """
        Download audio from video URL.

        Args:
            url: Video URL to download audio from
            output_path: Optional path for output file (temp file if None)

        Returns:
            Path to downloaded audio file

        Raises:
            VideoExtractionError: If download fails

        Example:
            >>> extractor = VideoExtractor()
            >>> audio_path = await extractor.download_audio("https://youtube.com/...")
            >>> # Use audio_path for transcription
        """
        try:
            if output_path is None:
                # Create temp file for audio
                temp_dir = Path(tempfile.mkdtemp())
                output_path = temp_dir / "audio.mp3"

            loop = asyncio.get_event_loop()
            audio_path = await loop.run_in_executor(
                None, self._download_audio_sync, url, output_path
            )
            return audio_path
        except Exception as e:
            raise VideoExtractionError(
                message=f"Failed to download audio: {str(e)}",
                details={"url": url, "error": str(e)},
            ) from e

    def _download_audio_sync(self, url: str, output_path: Path) -> Path:
        """Synchronous audio download (runs in executor)."""
        ydl_opts = {
            **self.ydl_opts,
            "outtmpl": str(output_path.with_suffix("")),  # yt-dlp adds extension
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # yt-dlp adds .mp3 extension
        final_path = output_path.with_suffix(".mp3")
        if not final_path.exists():
            raise VideoExtractionError(
                message="Audio file not found after download",
                details={"expected_path": str(final_path)},
            )

        return final_path

    def _detect_platform(self, url: str, info: dict[str, Any]) -> VideoPlatform:
        """
        Detect video platform from URL and metadata.

        Args:
            url: Video URL
            info: yt-dlp info dict

        Returns:
            VideoPlatform enum value
        """
        try:
            return platform_detector.detect_platform(url)
        except ValueError:
            return VideoPlatform.DIRECT

    def validate_url(self, url: str) -> bool:
        """
        Validate if URL is supported for video extraction.

        Args:
            url: Video URL to validate

        Returns:
            True if URL is valid and supported

        Example:
            >>> extractor = VideoExtractor()
            >>> extractor.validate_url("https://youtube.com/watch?v=...")
            True
        """
        try:
            platform = platform_detector.detect_platform(url)
            if not validate_platform_url(url, platform):
                return False

            # Quick validation without full extraction
            with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return info is not None
        except Exception:
            return False


# Global instance
video_extractor = VideoExtractor()
