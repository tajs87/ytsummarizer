from datetime import UTC, datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from src.api import deps
from src.main import app
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
    def __init__(self):
        self.videos = []
        self.next_id = 1

    def query(self, model):
        if model is Video:
            return FakeQuery(self.videos)
        return FakeQuery([])

    def add(self, obj):
        if getattr(obj, "id", None) is None:
            obj.id = self.next_id
            self.next_id += 1
        if getattr(obj, "created_at", None) is None:
            obj.created_at = datetime.now(UTC)
        self.videos.append(obj)

    def commit(self):
        return None

    def refresh(self, obj):
        if getattr(obj, "id", None) is None:
            obj.id = self.next_id
            self.next_id += 1
        if getattr(obj, "created_at", None) is None:
            obj.created_at = datetime.now(UTC)


class FakeSig:
    def __or__(self, other):
        return self

    def apply_async(self):
        return SimpleNamespace(id="task-integrated")


class FakeTask:
    def s(self, *args, **kwargs):
        return FakeSig()


def test_video_submission_flow_creates_pending_video(monkeypatch):
    fake_db = FakeDBSession()
    user = User(
        id=1, email="test@example.com", hashed_password="x", is_active=True, is_superuser=False
    )

    async def fake_get_db():
        yield fake_db

    async def fake_get_current_user():
        return user

    async def fake_extract_metadata(url: str):
        return {
            "platform": VideoPlatform.YOUTUBE,
            "title": "Integration Test Video",
            "duration_seconds": 120,
        }

    monkeypatch.setattr("src.api.v1.videos.video_extractor.extract_metadata", fake_extract_metadata)
    monkeypatch.setattr("src.api.v1.videos.extract_video_task", FakeTask())
    monkeypatch.setattr("src.api.v1.videos.transcribe_audio_task", FakeTask())

    app.dependency_overrides[deps.get_db] = fake_get_db
    app.dependency_overrides[deps.get_current_user] = fake_get_current_user
    app.dependency_overrides[deps.get_current_active_user] = fake_get_current_user

    client = TestClient(app)
    res = client.post("/api/v1/videos", json={"url": "https://www.youtube.com/watch?v=jNQXAC9IVRw"})

    assert res.status_code == 202
    assert len(fake_db.videos) == 1
    saved = fake_db.videos[0]
    assert saved.status == VideoStatus.PENDING
    assert saved.task_id == "task-integrated"

    app.dependency_overrides.clear()
