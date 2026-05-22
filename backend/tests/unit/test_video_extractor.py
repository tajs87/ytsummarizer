from src.models.video import VideoPlatform
from src.services.video_extractor import VideoExtractor


def test_detect_platform_from_urls():
    extractor = VideoExtractor()

    assert (
        extractor._detect_platform("https://www.youtube.com/watch?v=jNQXAC9IVRw", {})
        == VideoPlatform.YOUTUBE
    )
    assert extractor._detect_platform("https://vimeo.com/123456", {}) == VideoPlatform.VIMEO
    assert (
        extractor._detect_platform("https://cdn.example.com/video.mp4", {}) == VideoPlatform.DIRECT
    )


def test_validate_url_uses_platform_and_downloader(monkeypatch):
    extractor = VideoExtractor()

    class FakeYDL:
        def __init__(self, opts):
            self.opts = opts

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def extract_info(self, url, download=False):
            return {"id": "abc"}

    monkeypatch.setattr("src.services.video_extractor.yt_dlp.YoutubeDL", FakeYDL)

    assert extractor.validate_url("https://www.youtube.com/watch?v=jNQXAC9IVRw") is True
