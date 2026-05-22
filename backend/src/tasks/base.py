"""
Base task class with progress tracking for WebSocket updates.
"""
from typing import Any

from celery import Task

from src.tasks.app import celery_app


class ProgressTask(Task):
    """
    Base task class that supports progress tracking.
    
    Subclasses can call self.update_progress() to emit progress updates
    that will be sent to clients via WebSocket.
    
    Example:
        @app.task(base=ProgressTask, bind=True)
        def my_task(self, video_id: int):
            self.update_progress(10, "Starting extraction...")
            # ... do work ...
            self.update_progress(50, "Extracting audio...")
            # ... more work ...
            self.update_progress(100, "Complete!")
    """

    def update_progress(
        self,
        progress: int,
        stage: str,
        message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Update task progress.
        
        Args:
            progress: Progress percentage (0-100)
            stage: Current processing stage name
            message: Optional status message
            metadata: Optional additional metadata
        """
        self.update_state(
            state="PROGRESS",
            meta={
                "progress": progress,
                "stage": stage,
                "message": message or stage,
                "metadata": metadata or {},
            },
        )

    def on_failure(
        self,
        exc: Exception,
        task_id: str,
        args: tuple,  # type: ignore
        kwargs: dict[str, Any],
        einfo: Any,
    ) -> None:
        """
        Handle task failure by updating state.
        
        Args:
            exc: Exception that caused failure
            task_id: Task ID
            args: Task positional arguments
            kwargs: Task keyword arguments
            einfo: Exception info
        """
        self.update_state(
            state="FAILURE",
            meta={
                "error": str(exc),
                "error_type": type(exc).__name__,
                "args": args,
                "kwargs": kwargs,
            },
        )
        super().on_failure(exc, task_id, args, kwargs, einfo)


# Make ProgressTask available for task decorators
celery_app.Task = ProgressTask  # type: ignore
