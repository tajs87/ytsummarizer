"""
Video extraction service using yt-dlp.
Handles downloading audio and extracting metadata from video URLs.
"""

import asyncio
import base64
import os
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
        
        # Try to configure cookies to avoid YouTube bot detection
        self._configure_cookies()
    
    def _configure_cookies(self) -> None:
        """Configure cookie authentication for yt-dlp."""
        # Option 1: Use base64-encoded cookies from environment (for Railway/cloud)
        cookies_b64 = os.getenv("YTDLP_COOKIES_BASE64")
        if cookies_b64:
            try:
                # Decode and write to temp file
                cookie_content = base64.b64decode(cookies_b64).decode("utf-8")
                temp_cookie_file = Path(tempfile.gettempdir()) / "ytdlp_cookies.txt"
                temp_cookie_file.write_text(cookie_content)
                self.ydl_opts["cookiefile"] = str(temp_cookie_file)
                return
            except Exception:
                pass  # Fall through to next option
        
        # Option 2: Use cookie file if provided via environment variable
        cookie_file = os.getenv("YTDLP_COOKIE_FILE")
        if cookie_file and Path(cookie_file).exists():
            self.ydl_opts["cookiefile"] = cookie_file
            return
        
        # Option 3: Try to extract cookies from browser (for local development only)
        # Only attempt if explicitly enabled via environment variable
        if os.getenv("YTDLP_USE_BROWSER_COOKIES") == "true":
            for browser in ["chrome", "firefox", "safari", "edge"]:
                try:
                    self.ydl_opts["cookiesfrombrowser"] = (browser,)
                    # Browser found, will be validated on first use
                    return
                except Exception:
                    continue
        
        # If no cookies available, proceed without them
        # yt-dlp will work for most videos, but may fail on some YouTube videos

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
        # Start with lower bitrate to avoid file size issues
        # OpenAI Whisper API has 25MB limit
        ydl_opts = {
            **self.ydl_opts,
            "outtmpl": str(output_path.with_suffix("")),  # yt-dlp adds extension
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "96",  # Lower bitrate to stay under 25MB
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

        # Check file size and compress further if needed
        max_size = 24 * 1024 * 1024  # 24MB to be safe
        if final_path.stat().st_size > max_size:
            final_path = self._compress_audio(final_path, max_size)

        return final_path

    def _compress_audio(self, audio_path: Path, max_size: int) -> Path:
        """
        Compress audio file to fit under max size.

        Args:
            audio_path: Path to audio file to compress
            max_size: Maximum file size in bytes

        Returns:
            Path to compressed audio file

        Raises:
            VideoExtractionError: If compression fails
        """
        import subprocess

        compressed_path = audio_path.with_stem(f"{audio_path.stem}_compressed")
        
        # Calculate target bitrate based on duration
        # Leave some buffer for container overhead
        try:
            # Get audio duration using ffprobe
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    str(audio_path),
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            duration = float(result.stdout.strip())
            
            # Calculate target bitrate (in kbps), with 90% of max to be safe
            target_bitrate = int((max_size * 0.9 * 8) / (duration * 1000))
            target_bitrate = max(32, min(target_bitrate, 96))  # Clamp between 32-96 kbps
            
            # Compress using ffmpeg
            subprocess.run(
                [
                    "ffmpeg",
                    "-i", str(audio_path),
                    "-b:a", f"{target_bitrate}k",
                    "-ac", "1",  # Convert to mono
                    "-ar", "16000",  # Lower sample rate
                    str(compressed_path),
                    "-y",  # Overwrite output file
                ],
                capture_output=True,
                check=True,
            )
            
            # Remove original and return compressed
            audio_path.unlink()
            return compressed_path
            
        except Exception as e:
            raise VideoExtractionError(
                message=f"Failed to compress audio: {str(e)}",
                details={"audio_path": str(audio_path), "error": str(e)},
            ) from e

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
