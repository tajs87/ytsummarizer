#!/bin/bash
# Railway startup script - runs both FastAPI and Celery worker

set -e

echo "Starting Celery worker in background..."
celery -A src.tasks.app:celery_app worker --loglevel=info --concurrency=2 &

# Give Celery a moment to start
sleep 2

echo "Starting FastAPI server..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000
