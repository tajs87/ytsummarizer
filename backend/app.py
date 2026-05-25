"""
Celery app entry point for the worker process.

Exposes the Celery application as `celery` so the worker can be started with:
    celery -A app worker --loglevel=info
"""

from src.tasks.app import celery_app as celery  # noqa: F401
