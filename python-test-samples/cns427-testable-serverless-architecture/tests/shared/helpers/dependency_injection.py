"""Dependency injection helpers for different test scenarios."""

from contextlib import contextmanager

from task_api.domain.task_service import TaskService
from task_api.integration.factory import create_task_repository

from tests.shared.fakes import InMemoryEventPublisher, InMemoryTaskRepository


@contextmanager
def dynamodb_integration_dependencies():
    """
    Context manager for DynamoDB integration tests with mixed dependencies:
    - Real DynamoDB repository (tests actual data persistence)
    - Fake EventBridge publisher (avoids external calls, enables verification)

    Usage:
        with dynamodb_integration_dependencies() as event_publisher:
            response = lambda_handler(event, context)
            # Verify real DynamoDB persistence
            # Verify captured events in event_publisher
    """
    # Create real repository (uses actual DynamoDB table)
    real_repository = create_task_repository()

    # Create fake publisher (captures events in memory)
    fake_publisher = InMemoryEventPublisher()

    # Create TaskService with mixed dependencies
    mixed_service = TaskService(real_repository, fake_publisher)

    # Import handler module
    import task_api.handlers.task_handler as handler_module

    # Store original service
    original_service = getattr(handler_module, 'task_service', None)

    try:
        # Inject mixed service directly into handler
        handler_module.task_service = mixed_service

        yield fake_publisher  # Return publisher for event verification
    finally:
        # Restore original state for test isolation
        handler_module.task_service = original_service


@contextmanager
def eventbridge_integration_dependencies():
    """
    Context manager for EventBridge integration tests with mixed dependencies:
    - Fake DynamoDB repository (avoids database dependencies)
    - Real EventBridge publisher (tests actual event publishing)

    Usage:
        with eventbridge_integration_dependencies() as (repository, test_run_id):
            response = lambda_handler(event, context)
            # Verify fake repository state
            # Verify real EventBridge events using test_run_id
    """
    import os
    import uuid
    from unittest.mock import patch

    # Generate unique test run ID for event isolation
    test_run_id = f'test-{uuid.uuid4()}'

    # Create fake repository (avoids DynamoDB dependencies)
    fake_repository = InMemoryTaskRepository()

    # Create real publisher (tests actual EventBridge publishing)
    from task_api.integration.factory import create_event_publisher

    real_publisher = create_event_publisher()

    # Create TaskService with mixed dependencies
    mixed_service = TaskService(fake_repository, real_publisher)

    # Import handler module
    import task_api.handlers.task_handler as handler_module

    # Store original service
    original_service = getattr(handler_module, 'task_service', None)

    # Test configuration
    TEST_EVENT_BUS_NAME = os.environ.get('TEST_EVENT_BUS_NAME', 'cns427-task-api-test-bus')
    AWS_REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')

    try:
        # Set environment for test isolation
        with patch.dict(os.environ, {'EVENT_BUS_NAME': TEST_EVENT_BUS_NAME, 'AWS_DEFAULT_REGION': AWS_REGION}):
            # Inject mixed service directly into handler
            handler_module.task_service = mixed_service

            yield fake_repository, test_run_id
    finally:
        # Restore original state for test isolation
        handler_module.task_service = original_service


@contextmanager
def domain_unit_dependencies():
    """
    Context manager for domain unit tests with all fake dependencies:
    - Fake task repository (complete isolation from DynamoDB)
    - Fake event publisher (complete isolation from EventBridge)

    Usage:
        with domain_unit_dependencies() as (repository, publisher):
            service = TaskService(repository, publisher)
            # Test pure business logic
    """
    # Create all fake dependencies
    fake_repository = InMemoryTaskRepository()
    fake_publisher = InMemoryEventPublisher()

    try:
        yield fake_repository, fake_publisher
    finally:
        # Clean up for test isolation
        fake_repository.clear()
        fake_publisher.clear()
