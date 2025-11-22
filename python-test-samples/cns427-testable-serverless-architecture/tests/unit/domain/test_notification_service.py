"""Unit tests for notification service domain logic."""

import pytest

from services.notification_service.domain.notification_service import NotificationService
from tests.unit.test_helpers import create_task_event_detail


class TestNotificationService:
    """Unit tests for notification service pure business logic using fakes."""

    @pytest.fixture(autouse=True)
    def setup_env(self, monkeypatch):
        """Set up environment variables for tests."""
        monkeypatch.setenv('POWERTOOLS_SERVICE_NAME', 'notification-service-test')
        monkeypatch.setenv('LOG_LEVEL', 'INFO')

    @pytest.fixture
    def notification_service(self):
        """Create notification service instance."""
        return NotificationService()

    def test_process_task_created_event(self, notification_service, caplog):
        """Test processing TaskCreated event logs correct information."""
        # GIVEN a TaskCreated event data
        event_data = create_task_event_detail(task_id='test-task-123', title='Test Task', status='pending', priority='high')

        # WHEN processing the event
        notification_service.process_task_event('TaskCreated', event_data)

        # THEN should log task created notification
        assert 'Processing task event: TaskCreated' in caplog.text
        assert 'Task created notification: Test Task' in caplog.text
        # task_id is in structured logging extra fields, not in caplog.text
        assert len(caplog.records) >= 2

    def test_process_task_updated_event(self, notification_service, caplog):
        """Test processing TaskUpdated event logs status change."""
        # GIVEN a TaskUpdated event data
        event_data = create_task_event_detail(task_id='updated-task-456', title='Updated Task', status='completed', priority='medium')

        # WHEN processing the event
        notification_service.process_task_event('TaskUpdated', event_data)

        # THEN should log task updated notification with status
        assert 'Processing task event: TaskUpdated' in caplog.text
        assert 'Task updated notification: Updated Task (status: completed)' in caplog.text
        # task_id is in structured logging extra fields, not in caplog.text
        assert len(caplog.records) >= 2

    def test_process_task_deleted_event(self, notification_service, caplog):
        """Test processing TaskDeleted event logs deletion."""
        # GIVEN a TaskDeleted event data (only task_id)
        event_data = {'task_id': 'deleted-task-789'}

        # WHEN processing the event
        notification_service.process_task_event('TaskDeleted', event_data)

        # THEN should log task deleted notification
        assert 'Task deleted notification: deleted-task-789' in caplog.text
        assert 'deleted-task-789' in caplog.text

    def test_process_unknown_event_type_ignored(self, notification_service, caplog):
        """Test that unknown event types log a warning."""
        # GIVEN an event with unknown type
        event_data = {'task_id': 'unknown-task-id'}

        # WHEN processing the unknown event
        notification_service.process_task_event('UnknownEventType', event_data)

        # THEN should log a warning about unknown event type
        assert 'Processing task event: UnknownEventType' in caplog.text
        assert 'Unknown event type: UnknownEventType' in caplog.text

    def test_process_multiple_events_different_types(self, notification_service, caplog):
        """Test processing multiple events of different types."""
        # GIVEN multiple events of different types
        created_event_data = create_task_event_detail(task_id='task-1', title='Task 1', status='pending', priority='medium')

        updated_event_data = create_task_event_detail(task_id='task-2', title='Task 2', status='in_progress', priority='high')

        deleted_event_data = {'task_id': 'task-3'}

        # WHEN processing all events
        notification_service.process_task_event('TaskCreated', created_event_data)
        notification_service.process_task_event('TaskUpdated', updated_event_data)
        notification_service.process_task_event('TaskDeleted', deleted_event_data)

        # THEN all should log appropriate notifications
        assert 'Task created notification: Task 1' in caplog.text
        assert 'Task updated notification: Task 2' in caplog.text
        assert 'Task deleted notification: task-3' in caplog.text
