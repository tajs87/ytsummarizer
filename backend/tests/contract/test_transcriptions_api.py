from datetime import UTC, datetime

from fastapi.testclient import TestClient

from src.api import deps
from src.main import app
from src.models.transcription import Transcription
from src.models.user import User
from src.models.video import Video, VideoPlatform, VideoStatus


class FakeQuery:
    def __init__(self, items):
        self.items = items

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.items[0] if self.items else None


class FakeDBSession:
    def __init__(self, video, transcription):
        self.video = video
        self.transcription = transcription

    def query(self, model):
        if model is Video:
            return FakeQuery([self.video])
        if model is Transcription:
            return FakeQuery([self.transcription])
        return FakeQuery([])


def test_get_transcription_contract():
    user = User(
        id=1, email="test@example.com", hashed_password="x", is_active=True, is_superuser=False
    )
    video = Video(
        id=1,
        user_id=1,
        url="https://www.youtube.com/watch?v=jNQXAC9IVRw",
        url_hash=Video.generate_url_hash("https://www.youtube.com/watch?v=jNQXAC9IVRw"),
        platform=VideoPlatform.YOUTUBE,
        status=VideoStatus.COMPLETED,
    )
    transcription = Transcription(
        id=1,
        video_id=1,
        full_text="hello world",
        segments=[{"id": 0, "start": 0.0, "end": 1.5, "text": "hello world"}],
        language="en",
        word_count=2,
        created_at=datetime.now(UTC),
    )
    db = FakeDBSession(video, transcription)

    async def fake_get_db():
        yield db

    async def fake_get_current_user():
        return user

    app.dependency_overrides[deps.get_db] = fake_get_db
    app.dependency_overrides[deps.get_current_active_user] = fake_get_current_user

    client = TestClient(app)
    res = client.get("/api/v1/videos/1/transcription")

    assert res.status_code == 200
    data = res.json()
    assert data["video_id"] == 1
    assert data["full_text"] == "hello world"
    assert data["segments"][0]["text"] == "hello world"

    app.dependency_overrides.clear()
