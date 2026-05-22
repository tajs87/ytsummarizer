"""
Celery application configuration for async task processing.
"""
from celery import Celery

from src.core.config import get_settings

settings = get_settings()

# Create Celery app
celery_app = Celery(
    "ytsum",
    broker=str(settings.celery_broker_url),
    backend=str(settings.celery_result_backend),
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=1,  # Disable prefetching for long tasks
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks (prevent memory leaks)
)

# Auto-discover tasks from modules
celery_app.autodiscover_tasks(["src.tasks"])

# Import tasks to ensure they're registered
from src.tasks import extract, extract_highlights, summarize, transcribe  # noqa: E402, F401
