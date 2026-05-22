"""
Platform-specific URL validators for video submission.
"""

from urllib.parse import urlparse, parse_qs

from src.models.video import VideoPlatform


def validate_platform_url(url: str, platform: VideoPlatform) -> bool:
    """
    Validate URL format based on detected platform.

    Args:
        url: URL to validate
        platform: Detected platform

    Returns:
        True if URL is valid for platform
    """
    parsed = urlparse(url)

    if not parsed.scheme or parsed.scheme not in ["http", "https"]:
        return False

    if platform == VideoPlatform.YOUTUBE:
        return _validate_youtube_url(parsed)
    if platform == VideoPlatform.VIMEO:
        return _validate_vimeo_url(parsed)
    if platform == VideoPlatform.DIRECT:
        return _validate_direct_url(parsed)

    return False


def _validate_youtube_url(parsed) -> bool:
    """Validate YouTube URL format."""
    domain = parsed.netloc.replace("www.", "").lower()

    if domain == "youtu.be":
        # Short URL format: youtu.be/VIDEO_ID
        return bool(parsed.path and parsed.path != "/")

    if domain in ["youtube.com", "m.youtube.com"]:
        # Standard format: youtube.com/watch?v=VIDEO_ID
        if parsed.path == "/watch":
            query_params = parse_qs(parsed.query)
            return "v" in query_params and bool(query_params["v"][0])

        # Embed format: youtube.com/embed/VIDEO_ID
        if parsed.path.startswith("/embed/"):
            return len(parsed.path.split("/")) >= 3

    return False


def _validate_vimeo_url(parsed) -> bool:
    """Validate Vimeo URL format."""
    domain = parsed.netloc.replace("www.", "").lower()

    if domain == "vimeo.com":
        # Format: vimeo.com/VIDEO_ID
        path_parts = [p for p in parsed.path.split("/") if p]
        return len(path_parts) >= 1 and path_parts[0].isdigit()

    if domain == "player.vimeo.com":
        # Embed format: player.vimeo.com/video/VIDEO_ID
        path_parts = [p for p in parsed.path.split("/") if p]
        return len(path_parts) >= 2 and path_parts[0] == "video" and path_parts[1].isdigit()

    return False


def _validate_direct_url(parsed) -> bool:
    """Validate direct video URL format."""
    # Must have valid domain
    if not parsed.netloc:
        return False

    # Check for video file extensions
    video_extensions = [".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".m4v"]
    if any(parsed.path.lower().endswith(ext) for ext in video_extensions):
        return True

    # Allow URLs with video-like paths
    video_path_indicators = ["video", "media", "stream", "content"]
    path_lower = parsed.path.lower()
    return any(indicator in path_lower for indicator in video_path_indicators)
