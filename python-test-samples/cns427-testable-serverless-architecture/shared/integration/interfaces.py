"""Core interfaces for the task management API."""

from abc import ABC, abstractmethod
from typing import List, Optional

from services.task_service.models.task import Task, TaskEvent


class TaskRepository(ABC):
    """Interface for task data persistence."""

    @abstractmethod
    def create_task(self, task: Task) -> Task:
        """Create a new task."""
        pass

    @abstractmethod
    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by ID."""
        pass

    @abstractmethod
    def list_tasks(self, limit: int = 50, next_token: Optional[str] = None) -> tuple[List[Task], Optional[str]]:
        """List tasks with pagination."""
        pass

    @abstractmethod
    def update_task(self, task: Task, expected_version: int) -> Task:
        """
        Update an existing task with optimistic locking.

        Args:
            task: The task with updated fields and new version
            expected_version: The old version to check against

        Returns:
            The updated task
        """
        pass

    @abstractmethod
    def delete_task(self, task_id: str, version: int) -> None:
        """Delete a task."""
        pass


class EventPublisher(ABC):
    """Interface for publishing task events."""

    @abstractmethod
    def publish_event(self, event: TaskEvent) -> None:
        """Publish a task event."""
        pass
