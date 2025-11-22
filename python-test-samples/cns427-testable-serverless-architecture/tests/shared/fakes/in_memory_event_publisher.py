"""In-memory fake implementation of EventPublisher for all test types."""

from typing import List

from task_api.models.interfaces import EventPublisher
from task_api.models.task import TaskEvent


class InMemoryEventPublisher(EventPublisher):
    """
    In-memory implementation of EventPublisher for testing.

    This fake captures events in memory instead of publishing to EventBridge,
    making it suitable for both unit tests (complete isolation) and integration
    tests (real DynamoDB + fake EventBridge).
    """

    def __init__(self):
        """Initialize with empty event storage."""
        self.published_events: List[TaskEvent] = []

    def publish_event(self, event: TaskEvent) -> None:
        """Store event in memory instead of publishing to EventBridge."""
        self.published_events.append(event)

    def clear(self) -> None:
        """Clear all published events (useful for test cleanup)."""
        self.published_events.clear()

    def count(self) -> int:
        """Get total number of published events."""
        return len(self.published_events)

    def get_events_by_type(self, event_type) -> List[TaskEvent]:
        """Get events filtered by type."""
        return [event for event in self.published_events if event.event_type == event_type]

    def get_latest_event(self) -> TaskEvent:
        """Get the most recently published event."""
        if not self.published_events:
            raise ValueError('No events have been published')
        return self.published_events[-1]

    def has_event_with_task_id(self, task_id: str) -> bool:
        """Check if any event exists for the given task ID."""
        return any(event.task_id == task_id for event in self.published_events)
