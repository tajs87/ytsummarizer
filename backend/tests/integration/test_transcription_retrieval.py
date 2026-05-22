from datetime import datetime, timezone

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


def test_transcription_retrieval_and_search_flow():
    user = User(id=1, email="test@example.com", hashed_password="x", is_active=True, is_superuser=False)
    video = Video(
        id=1,
        user_id=1,
        url="https://www.youtube.com/watch?v=jNQXAC9IVRw",
        url_hash=Video.generate_url_hash("https://www.youtube.com/watch?v=jNQXAC9IVRw"),
        platform=VideoPlatform.YOUTUBE,
        status=VideoStatus.COMPLETED,
        title="Retriever",
    )
    transcription = Transcription(
        id=1,
        video_id=1,
        full_text="hello world from test",
        segments=[
            {"id": 0, "start": 0.0, "end": 1.0, "text": "hello world"},
            {"id": 1, "start": 1.0, "end": 2.0, "text": "from test"},
        ],
        language="en",
        word_count=4,
        created_at=datetime.now(timezone.utc),
    )

    db = FakeDBSession(video, transcription)

    async def fake_get_db():
        yield db

    async def fake_get_current_user():
        return user

    app.dependency_overrides[deps.get_db] = fake_get_db
    app.dependency_overrides[deps.get_current_active_user] = fake_get_current_user

    client = TestClient(app)

    get_res = client.get("/api/v1/videos/1/transcription")
    assert get_res.status_code == 200
    assert get_res.json()["word_count"] == 4

    search_res = client.post("/api/v1/videos/1/transcription/search", json={"query": "hello"})
    assert search_res.status_code == 200
    assert search_res.json()["total_matches"] == 1

    app.dependency_overrides.clear()
