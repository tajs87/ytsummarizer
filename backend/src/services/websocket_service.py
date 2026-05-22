"""
WebSocket manager for broadcasting progress updates.
Manages connections and message distribution to connected clients.
"""
from typing import Any

from fastapi import WebSocket


class WebSocketManager:
    """
    Manages WebSocket connections and broadcasts progress updates.

    Maintains a mapping of task_id -> list of connected WebSockets.
    """

    def __init__(self) -> None:
        """Initialize connection manager."""
        # Map task_id -> list of WebSocket connections
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, task_id: str) -> None:
        """
        Accept and register a WebSocket connection.

        Args:
            websocket: WebSocket connection to register
            task_id: Celery task ID to associate with connection
        """
        await websocket.accept()

        if task_id not in self.active_connections:
            self.active_connections[task_id] = []

        self.active_connections[task_id].append(websocket)

    def disconnect(self, websocket: WebSocket, task_id: str) -> None:
        """
        Remove WebSocket connection.

        Args:
            websocket: WebSocket connection to remove
            task_id: Associated task ID
        """
        if task_id in self.active_connections:
            self.active_connections[task_id].remove(websocket)

            # Clean up empty task lists
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]

    async def broadcast_progress(
        self, task_id: str, progress: int, message: str, status: str = "processing"
    ) -> None:
        """
        Broadcast progress update to all clients watching a task.

        Args:
            task_id: Celery task ID
            progress: Progress percentage (0-100)
            message: Status message
            status: Task status (processing, completed, failed)

        Example:
            >>> await websocket_manager.broadcast_progress(
            ...     "abc-123",
            ...     45,
            ...     "Transcribing audio...",
            ...     "processing"
            ... )
        """
        if task_id not in self.active_connections:
            return

        payload = {
            "progress": progress,
            "message": message,
            "status": status,
        }

        # Send to all connected clients
        disconnected = []
        for connection in self.active_connections[task_id]:
            try:
                await connection.send_json(payload)
            except Exception:
                # Mark for removal if send fails
                disconnected.append(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection, task_id)

    async def send_completion(
        self, task_id: str, success: bool, message: str, data: dict[str, Any] | None = None
    ) -> None:
        """
        Send completion message to clients.

        Args:
            task_id: Celery task ID
            success: Whether task completed successfully
            message: Completion message
            data: Optional result data
        """
        await self.broadcast_progress(
            task_id,
            100,
            message,
            status="completed" if success else "failed",
        )


# Global WebSocket manager instance
websocket_manager = WebSocketManager()
