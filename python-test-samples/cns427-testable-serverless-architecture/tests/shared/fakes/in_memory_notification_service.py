"""In-memory fake implementation of NotificationService for all test types."""

from typing import List

from task_api.models.task import TaskEvent, TaskEventType


class InMemoryNotificationService:
    """
    In-memory implementation of NotificationService for testing.

    This fake captures processed events in memory instead of logging,
    making it suitable for unit tests that need to verify notification
    processing behavior.
    """

    def __init__(self):
        """Initialize with empty notification storage."""
        self.processed_events: List[TaskEvent] = []
        self.created_notifications: List[TaskEvent] = []
        self.updated_notifications: List[TaskEvent] = []
        self.deleted_notifications: List[TaskEvent] = []

    def process_task_event(self, task_event: TaskEvent) -> None:
        """Process a task event and store notification instead of logging."""
        self.processed_events.append(task_event)

        if task_event.event_type == TaskEventType.TASK_CREATED:
            self._handle_task_created(task_event)
        elif task_event.event_type == TaskEventType.TASK_UPDATED:
            self._handle_task_updated(task_event)
        elif task_event.event_type == TaskEventType.TASK_DELETED:
            self._handle_task_deleted(task_event)

    def _handle_task_created(self, task_event: TaskEvent) -> None:
        """Handle task created notification by storing it."""
        self.created_notifications.append(task_event)

    def _handle_task_updated(self, task_event: TaskEvent) -> None:
        """Handle task updated notification by storing it."""
        self.updated_notifications.append(task_event)

    def _handle_task_deleted(self, task_event: TaskEvent) -> None:
        """Handle task deleted notification by storing it."""
        self.deleted_notifications.append(task_event)

    def clear(self) -> None:
        """Clear all stored notifications (useful for test cleanup)."""
        self.processed_events.clear()
        self.created_notifications.clear()
        self.updated_notifications.clear()
        self.deleted_notifications.clear()

    def count_total(self) -> int:
        """Get total number of processed events."""
        return len(self.processed_events)

    def count_by_type(self, event_type: TaskEventType) -> int:
        """Get count of events by type."""
        return len([e for e in self.processed_events if e.event_type == event_type])

    def get_latest_event(self) -> TaskEvent:
        """Get the most recently processed event."""
        if not self.processed_events:
            raise ValueError('No events have been processed')
        return self.processed_events[-1]

    def has_event_with_task_id(self, task_id: str) -> bool:
        """Check if any event exists for the given task ID."""
        return any(event.task_id == task_id for event in self.processed_events)
