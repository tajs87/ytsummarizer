"""
WebSocket endpoint for real-time progress updates.
Provides live transcription progress to frontend clients.
"""

import asyncio
from typing import Any

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.services.websocket_service import websocket_manager
from src.tasks.app import celery_app

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/progress/{task_id}")
async def progress_websocket(
    websocket: WebSocket,
    task_id: str,
    db: Session = Depends(get_db),
) -> None:
    """
    WebSocket endpoint for receiving real-time task progress updates.

    Client connects with Celery task_id to receive progress messages.

    Message format:
    {
        "progress": 45,
        "message": "Transcribing audio...",
        "status": "processing"
    }

    Usage:
        ws = new WebSocket('ws://localhost:8000/api/v1/ws/progress/{task_id}')
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data)
            console.log(`Progress: ${data.progress}%`)
        }
    """
    await websocket_manager.connect(websocket, task_id)

    last_payload: dict[str, Any] | None = None

    try:
        # Poll Celery state and stream it to connected clients.
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                if data == "ping":
                    await websocket.send_json({"type": "pong"})
            except TimeoutError:
                pass

            result = AsyncResult(task_id, app=celery_app)
            meta = result.info if isinstance(result.info, dict) else {}

            payload: dict[str, Any]
            if result.state == "PROGRESS":
                payload = {
                    "progress": int(meta.get("progress", 0)),
                    "message": str(meta.get("message", "Processing...")),
                    "status": "processing",
                }
            elif result.state == "SUCCESS":
                payload = {
                    "progress": 100,
                    "message": "Processing complete",
                    "status": "completed",
                }
            elif result.state == "FAILURE":
                payload = {
                    "progress": int(meta.get("progress", 0)) if meta else 0,
                    "message": str(meta.get("error", "Processing failed"))
                    if meta
                    else "Processing failed",
                    "status": "failed",
                }
            elif result.state == "STARTED":
                payload = {
                    "progress": 5,
                    "message": "Task started",
                    "status": "processing",
                }
            else:
                payload = {
                    "progress": 0,
                    "message": "Initializing...",
                    "status": "processing",
                }

            if payload != last_payload:
                await websocket.send_json(payload)
                last_payload = payload

            if payload["status"] in {"completed", "failed"}:
                break

    except WebSocketDisconnect:
        pass
    finally:
        websocket_manager.disconnect(websocket, task_id)
