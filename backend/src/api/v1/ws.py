"""
WebSocket endpoint for real-time progress updates.
Provides live transcription progress to frontend clients.
"""
from typing import Any

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.services.websocket_service import websocket_manager

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
    
    try:
        # Keep connection alive and receive client messages
        while True:
            data = await websocket.receive_text()
            
            # Client can send "ping" to keep connection alive
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, task_id)
