"""
EventBridge Integration Tests

Tests EventPublisher against real EventBridge with test harness verification.
Uses fakes only for error simulation.
"""

import json
import os
import time
import uuid
from datetime import UTC, datetime
from unittest.mock import Mock

import boto3
import pytest

from infrastructure.config import InfrastructureConfig
from services.task_service.domain.task_service import TaskService
from services.task_service.models.task import Task, TaskPriority, TaskStatus
from shared.integration.dynamodb_adapter import DynamoDBTaskRepository
from shared.integration.eventbridge_adapter import EventBridgePublisher
from tests.integration.fakes.eventbridge_fake import EventBridgeFake
from tests.unit.test_helpers import create_api_gateway_event, create_test_context

# Real AWS resources from config
config = InfrastructureConfig()
EVENT_BUS_NAME = os.environ.get('EVENT_BUS_NAME', config.event_bus_name())
TEST_HARNESS_TABLE = os.environ.get('TEST_HARNESS_TABLE', config.test_results_table_name())
AWS_REGION = os.environ.get('AWS_DEFAULT_REGION', os.environ.get('AWS_REGION', 'us-west-2'))


@pytest.fixture
def test_run_id():
    """Generate unique test run ID for event correlation."""
    return str(uuid.uuid4())


@pytest.fixture
def dynamodb_client():
    """DynamoDB client for test harness verification."""
    return boto3.client('dynamodb', region_name=AWS_REGION)


@pytest.fixture
def test_task(test_run_id):
    """Create test task for event publishing."""
    now = datetime.now(UTC)
    return Task(
        task_id=str(uuid.uuid4()),
        title=f'TEST-{test_run_id}',
        description='Task for EventBridge testing',
        dependencies=[],
        status=TaskStatus.PENDING,
        priority=TaskPriority.MEDIUM,
        created_at=now,
        updated_at=now,
        version=int(now.timestamp() * 1000),
    )


def wait_for_event_processing(seconds=5):
    """Wait for EventBridge → Lambda → DynamoDB pipeline."""
    time.sleep(seconds)


def query_test_harness(dynamodb_client, test_run_id: str):
    """Query test harness table by test_run_id set to TEST-{test_run_id}."""
    response = dynamodb_client.query(
        TableName=TEST_HARNESS_TABLE,
        KeyConditionExpression='test_run_id = :test_run_id',
        ExpressionAttributeValues={':test_run_id': {'S': f'TEST-{test_run_id}'}},
    )
    return response.get('Items', [])


class TestEventBridgeIntegration:
    """Test EventPublisher with real EventBridge and test harness verification."""

    def test_publish_task_created_event(self, test_run_id, test_task, dynamodb_client):
        """Test task created event is published and appears in test harness."""
        # GIVEN EventPublisher with test event bus
        from services.task_service.models.task import TaskCreatedEvent

        publisher = EventBridgePublisher(event_bus_name=EVENT_BUS_NAME)

        # WHEN publishing TaskCreated event with TEST- prefix for test harness
        event = TaskCreatedEvent(test_task, source='TEST-cns427-task-api', detail_type_prefix='TEST-')
        publisher.publish_event(event)

        # Wait for event processing
        wait_for_event_processing()

        # THEN event should appear in test harness table
        events = query_test_harness(dynamodb_client, test_run_id)
        assert len(events) > 0, 'Event not found in test harness'

        # Verify event data
        event_item = events[0]
        assert event_item['test_run_id']['S'] == f'TEST-{test_run_id}'
        assert 'event_timestamp' in event_item

    def test_publish_event_with_dependencies(self, test_run_id, dynamodb_client):
        """Test event with task dependencies is published correctly."""
        # GIVEN task with dependencies
        from services.task_service.models.task import TaskCreatedEvent

        now = datetime.now(UTC)
        task = Task(
            task_id=str(uuid.uuid4()),
            title=f'TEST-{test_run_id}',
            description='Task with dependencies',
            dependencies=['task-1', 'task-2'],
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            created_at=now,
            updated_at=now,
            version=int(now.timestamp() * 1000),
        )
        publisher = EventBridgePublisher(event_bus_name=EVENT_BUS_NAME)

        # WHEN publishing event with TEST- prefix for test harness
        event = TaskCreatedEvent(task, source='TEST-cns427-task-api', detail_type_prefix='TEST-')
        publisher.publish_event(event)

        # Wait for event processing
        wait_for_event_processing()

        # THEN event should be in test harness
        events = query_test_harness(dynamodb_client, test_run_id)
        assert len(events) > 0

    def test_publish_multiple_events(self, test_run_id, dynamodb_client):
        """Test multiple events are published and tracked separately."""
        # GIVEN multiple tasks with same test_run_id in title for tracking
        from services.task_service.models.task import TaskCreatedEvent

        now = datetime.now(UTC)
        tasks = [
            Task(
                task_id=str(uuid.uuid4()),
                title=f'TEST-{test_run_id}',
                description=f'Test task {i}',
                dependencies=[],
                status=TaskStatus.PENDING,
                priority=TaskPriority.MEDIUM,
                created_at=now,
                updated_at=now,
                version=int(now.timestamp() * 1000),
            )
            for i in range(3)
        ]
        publisher = EventBridgePublisher(event_bus_name=EVENT_BUS_NAME)

        # WHEN publishing multiple events with TEST- prefix for test harness
        for task in tasks:
            event = TaskCreatedEvent(task, source='TEST-cns427-task-api', detail_type_prefix='TEST-')
            publisher.publish_event(event)

        wait_for_event_processing()

        # THEN all events should be in test harness
        events = query_test_harness(dynamodb_client, test_run_id)
        assert len(events) >= 3


@pytest.fixture
def fake_task_service_with_eventbridge_error(request):
    """Fixture to inject fake TaskService with EventBridge error simulation."""
    error_type = request.param if hasattr(request, 'param') else 'throttling'

    # Create mock repository (no errors)
    fake_repo = Mock()

    # Create fake event publisher with error
    fake_publisher = EventBridgePublisher(event_bus_name=EVENT_BUS_NAME)
    fake_publisher.events_client = EventBridgeFake(error_type)

    # Create service with fake repo and fake publisher
    fake_service = TaskService(fake_repo, fake_publisher)

    # Inject fake service into handler module
    import services.task_service.handler as handler_module

    handler_module.task_service = fake_service

    yield fake_service


class TestEventBridgeErrorSimulation:
    """Test EventBridge error handling through full handler integration."""

    @pytest.mark.parametrize('fake_task_service_with_eventbridge_error', ['throttling'], indirect=True)
    def test_throttling_error_returns_500_internal_error(self, fake_task_service_with_eventbridge_error):
        """Test that EventBridge throttling returns 500 Internal Server Error."""
        # GIVEN a system experiencing EventBridge throttling (injected via fixture)

        # WHEN client tries to create a task (which triggers event publishing)
        event = create_api_gateway_event(method='POST', path='/tasks', body={'title': 'New Task', 'description': 'Test'})

        lambda_context = create_test_context()
        from services.task_service.handler import lambda_handler

        response = lambda_handler(event, lambda_context)

        # THEN should return 500 Internal Server Error
        assert response['statusCode'] == 500, f'Expected 500 but got {response["statusCode"]}'

        # AND response should include generic error message (not expose EventBridge details)
        body = json.loads(response['body'])
        message = body.get('message', '').lower()
        assert 'internal' in message or 'error' in message, f'Expected generic internal error message but got: {body.get("message")}'
        # Ensure EventBridge-specific details are not exposed
        assert 'eventbridge' not in message and 'event bus' not in message, f'Should not expose EventBridge details: {body.get("message")}'

    @pytest.mark.parametrize('fake_task_service_with_eventbridge_error', ['permission'], indirect=True)
    def test_permission_error_returns_500_internal_error(self, fake_task_service_with_eventbridge_error):
        """Test that EventBridge permission errors return 500 Internal Server Error."""
        # GIVEN a system with EventBridge permission issues (injected via fixture)

        # WHEN client tries to create a task
        event = create_api_gateway_event(method='POST', path='/tasks', body={'title': 'New Task', 'description': 'Test'})

        lambda_context = create_test_context()
        from services.task_service.handler import lambda_handler

        response = lambda_handler(event, lambda_context)

        # THEN should return 500 Internal Server Error
        assert response['statusCode'] == 500, f'Expected 500 but got {response["statusCode"]}'

        # AND response should NOT expose permission details to client
        body = json.loads(response['body'])
        message = body.get('message', '').lower()
        assert 'permission' not in message and 'access' not in message, f'Should not expose permission details to client: {body.get("message")}'
        assert 'internal' in message or 'error' in message, f'Expected generic internal error message but got: {body.get("message")}'

    @pytest.mark.parametrize('fake_task_service_with_eventbridge_error', ['service'], indirect=True)
    def test_service_error_returns_500_internal_error(self, fake_task_service_with_eventbridge_error):
        """Test that EventBridge service errors return 500 Internal Server Error."""
        # GIVEN a system experiencing EventBridge service errors (injected via fixture)

        # WHEN client tries to create a task
        event = create_api_gateway_event(method='POST', path='/tasks', body={'title': 'New Task', 'description': 'Test'})

        lambda_context = create_test_context()
        from services.task_service.handler import lambda_handler

        response = lambda_handler(event, lambda_context)

        # THEN should return 500 Internal Server Error
        assert response['statusCode'] == 500, f'Expected 500 but got {response["statusCode"]}'

        # AND response should include generic error message
        body = json.loads(response['body'])
        message = body.get('message', '').lower()
        assert 'internal' in message or 'error' in message, f'Expected generic internal error message but got: {body.get("message")}'
