"""
Service for detecting video platform from URL.
Supports YouTube, Vimeo, and direct video links.
"""

from urllib.parse import urlparse

from src.models.video import VideoPlatform


class PlatformDetector:
    """Detects video platform based on URL patterns."""

    @staticmethod
    def detect_platform(url: str) -> VideoPlatform:
        """
        Detect platform from video URL.

        Args:
            url: Video URL to analyze

        Returns:
            Detected video platform

        Raises:
            ValueError: If platform is unsupported
        """
        parsed = urlparse(url.lower())
        domain = parsed.netloc.replace("www.", "")

        # YouTube detection
        if domain in ["youtube.com", "youtu.be", "m.youtube.com"]:
            return VideoPlatform.YOUTUBE

        # Vimeo detection
        if domain in ["vimeo.com", "player.vimeo.com"]:
            return VideoPlatform.VIMEO

        # Direct video URL detection by file extension
        video_extensions = [".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".m4v"]
        if any(parsed.path.endswith(ext) for ext in video_extensions):
            return VideoPlatform.DIRECT

        # Direct URL by query params indicating video content
        if any(param in parsed.query for param in ["video", "mp4", "stream"]):
            return VideoPlatform.DIRECT

        raise ValueError(f"Unsupported video platform for URL: {url}")


platform_detector = PlatformDetector()
