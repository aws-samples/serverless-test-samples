"""Unit tests for notification handler focusing on event processing and Lambda integration."""

import pytest

from services.notification_service.handler import lambda_handler
from tests.unit.test_helpers import create_eventbridge_event, create_test_context


@pytest.fixture
def lambda_context():
    """Fixture for Lambda context."""
    return create_test_context()


class TestNotificationHandler:
    """Unit tests for notification handler focusing on event processing and Lambda integration."""

    def test_lambda_handler_direct_eventbridge_event(self, fake_notification_service, lambda_context):
        """Test lambda handler with direct EventBridge event returns correct response."""
        # GIVEN direct EventBridge event
        event = create_eventbridge_event(detail_type='TaskCreated', task_id='test-task-id')

        # WHEN processing through lambda handler
        result = lambda_handler(event, lambda_context)

        # THEN should return success response
        assert result['statusCode'] == 200
        assert result['processedEvents'] == 1

        # AND should have processed one event
        assert len(fake_notification_service.processed_events) == 1

    def test_lambda_handler_task_updated_event(self, fake_notification_service, lambda_context):
        """Test lambda handler processing TaskUpdated event."""
        # GIVEN TaskUpdated EventBridge event
        event = create_eventbridge_event(detail_type='TaskUpdated', task_id='task-2', title='Updated Task', status='completed')

        # WHEN processing through lambda handler
        result = lambda_handler(event, lambda_context)

        # THEN should return success with correct processed count
        assert result['statusCode'] == 200
        assert result['processedEvents'] == 1

        # AND should have processed the event
        assert len(fake_notification_service.processed_events) == 1
        assert fake_notification_service.processed_events[0]['event_type'] == 'TaskUpdated'

    def test_lambda_handler_no_events(self, fake_notification_service, lambda_context):
        """Test lambda handler with no events returns zero count."""
        # GIVEN empty event
        event = {}

        # WHEN processing through lambda handler
        result = lambda_handler(event, lambda_context)

        # THEN should return success with zero processed count
        assert result['statusCode'] == 200
        assert result['processedEvents'] == 0

        # AND should not have processed any events
        assert len(fake_notification_service.processed_events) == 0

    def test_lambda_handler_processing_error_propagates(self, fake_notification_service, lambda_context):
        """Test lambda handler propagates processing errors."""
        # GIVEN event that will cause processing error
        event = create_eventbridge_event(detail_type='TaskCreated', task_id='error-task')

        # Configure fake service to raise an error
        fake_notification_service.should_raise_error = True

        # WHEN processing event that causes error
        # THEN should propagate the exception
        with pytest.raises(Exception, match='Notification processing failed'):
            lambda_handler(event, lambda_context)
