from datetime import UTC, datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from src.api import deps
from src.api.deps import RequestContext
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

    def count(self):
        return len(self.items)

    def order_by(self, *args, **kwargs):
        return self

    def offset(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def all(self):
        return list(self.items)


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
        return SimpleNamespace(id="task-123")


class FakeTask:
    def s(self, *args, **kwargs):
        return FakeSig()


def test_post_videos_contract(monkeypatch):
    fake_db = FakeDBSession()
    user = User(
        id=1, email="test@example.com", hashed_password="x", is_active=True, is_superuser=False
    )

    async def fake_get_db():
        yield fake_db

    async def fake_get_request_context():
        return RequestContext(user=user)

    async def fake_extract_metadata(url: str):
        return {
            "platform": VideoPlatform.YOUTUBE,
            "title": "Test Video",
            "duration_seconds": 60,
        }

    monkeypatch.setattr("src.api.v1.videos.video_extractor.extract_metadata", fake_extract_metadata)
    monkeypatch.setattr("src.api.v1.videos.extract_video_task", FakeTask())
    monkeypatch.setattr("src.api.v1.videos.transcribe_audio_task", FakeTask())

    app.dependency_overrides[deps.get_db] = fake_get_db
    app.dependency_overrides[deps.get_request_context] = fake_get_request_context

    client = TestClient(app)
    res = client.post("/api/v1/videos", json={"url": "https://www.youtube.com/watch?v=jNQXAC9IVRw"})

    assert res.status_code == 202
    data = res.json()
    assert data["id"] == 1
    assert data["status"] == VideoStatus.PENDING.value
    assert data["task_id"] == "task-123"
    assert data["platform"] == VideoPlatform.YOUTUBE.value

    app.dependency_overrides.clear()


def test_get_video_by_id_contract(monkeypatch):
    fake_db = FakeDBSession()
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
        task_id="task-1",
        title="Test",
        created_at=datetime.now(UTC),
    )
    fake_db.videos.append(video)

    async def fake_get_db():
        yield fake_db

    async def fake_get_request_context():
        return RequestContext(user=user)

    app.dependency_overrides[deps.get_db] = fake_get_db
    app.dependency_overrides[deps.get_request_context] = fake_get_request_context

    client = TestClient(app)
    res = client.get("/api/v1/videos/1")

    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 1
    assert data["url"] == video.url
    assert data["status"] == VideoStatus.COMPLETED.value

    app.dependency_overrides.clear()
