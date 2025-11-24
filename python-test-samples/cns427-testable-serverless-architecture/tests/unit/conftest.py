"""Unit test configuration - automatically disables socket connections."""

import pytest


@pytest.fixture(scope='session', autouse=True)
def disable_socket_for_unit_tests():
    """Automatically disable socket connections for all unit tests."""
    import pytest_socket

    pytest_socket.disable_socket()
    yield
    pytest_socket.enable_socket()


@pytest.fixture
def socket_disabled():
    """Fixture that indicates sockets are disabled.

    This fixture doesn't do anything itself - the actual socket disabling
    is handled by the disable_socket_for_unit_tests fixture above.
    This fixture is used in test signatures to make it explicit that
    the test requires socket disabling.
    """
    pass


"""Test configuration and fixtures."""
from datetime import UTC, datetime

import pytest

from services.task_service.domain.exceptions import CircularDependencyError, ConflictError
from services.task_service.models.api import CreateTaskRequest, UpdateTaskRequest
from services.task_service.models.task import Task, TaskPriority, TaskStatus


class FakeTaskService:
    """Fake TaskService for testing HTTP behavior."""

    def __init__(self):
        self.should_raise_circular_dependency = False
        self.should_raise_conflict_error = False
        self.should_raise_generic_error = False
        self.should_raise_value_error = False
        self.return_task = None
        self.return_none = False
        self.value_error_message = 'Task not found'

    def create_task(self, request: CreateTaskRequest) -> Task:
        """Create a task from CreateTaskRequest."""
        if self.should_raise_generic_error:
            raise Exception('Database connection failed')

        if self.should_raise_circular_dependency:
            raise CircularDependencyError('Circular dependency detected')

        # Return fake task
        task = Task(
            task_id='test-task-123',
            title=request.title,
            description=request.description,
            priority=request.priority,
            dependencies=request.dependencies,
            status=TaskStatus.PENDING,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            version=int(datetime.now(UTC).timestamp() * 1000),
        )
        return task

    def get_task(self, task_id: str) -> Task:
        """Get a task by ID."""
        if self.should_raise_generic_error:
            raise Exception('Database connection failed')

        if self.should_raise_value_error:
            raise ValueError(self.value_error_message)

        if self.return_none:
            raise ValueError(f'Task not found: {task_id}')

        if self.return_task:
            return self.return_task

        # Return fake task
        task = Task(
            task_id=task_id,
            title='Retrieved Task',
            description='Test task',
            priority=TaskPriority.MEDIUM,
            dependencies=[],
            status=TaskStatus.PENDING,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            version=int(datetime.now(UTC).timestamp() * 1000),
        )
        return task

    def list_tasks(self, limit: int = 50, next_token: str = None):
        """List tasks with pagination."""
        tasks = [
            Task(
                task_id='task-1',
                title='Task 1',
                description='First task',
                priority=TaskPriority.MEDIUM,
                dependencies=[],
                status=TaskStatus.PENDING,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                version=int(datetime.now(UTC).timestamp() * 1000),
            ),
            Task(
                task_id='task-2',
                title='Task 2',
                description='Second task',
                priority=TaskPriority.HIGH,
                dependencies=[],
                status=TaskStatus.IN_PROGRESS,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                version=int(datetime.now(UTC).timestamp() * 1000),
            ),
        ]
        return tasks, None  # Return tasks and next_token

    def update_task(self, task_id: str, request: UpdateTaskRequest) -> Task:
        """Update a task."""
        if self.should_raise_value_error:
            raise ValueError(self.value_error_message)

        if self.should_raise_circular_dependency:
            raise CircularDependencyError('Circular dependency detected')

        if self.should_raise_conflict_error:
            now = datetime.now(UTC)
            current_task_dict = {
                'task_id': task_id,
                'title': 'Current Task',
                'description': 'Current description',
                'priority': 'medium',
                'dependencies': [],
                'status': 'pending',
                'created_at': now.isoformat(),
                'updated_at': now.isoformat(),
                'version': 9876543210,
            }
            raise ConflictError('Task was modified by another process', current_task=current_task_dict)

        # Return updated task
        task = Task(
            task_id=task_id,
            title=request.title or 'Updated Task',
            description=request.description,
            priority=request.priority or TaskPriority.MEDIUM,
            dependencies=request.dependencies or [],
            status=TaskStatus(request.status) if request.status else TaskStatus.PENDING,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            version=int(datetime.now(UTC).timestamp() * 1000),
        )
        return task

    def delete_task(self, task_id: str) -> None:
        """Delete a task."""
        if self.should_raise_value_error:
            raise ValueError(self.value_error_message)

        if self.return_none:
            raise ValueError(f'Task not found: {task_id}')

        # Success - no return value


@pytest.fixture
def fake_task_service():
    """Create fake task service and inject it into handler."""
    fake_service = FakeTaskService()

    # Inject fake service into handler module
    import services.task_service.handler as handler

    original_service = handler.task_service
    handler.task_service = fake_service

    yield fake_service

    # Restore original service
    handler.task_service = original_service


class FakeNotificationService:
    """Fake NotificationService for testing HTTP behavior."""

    def __init__(self):
        self.should_raise_error = False
        self.processed_events = []

    def process_task_event(self, event_type: str, task_data: dict) -> None:
        """Process a task event and track it."""
        if self.should_raise_error:
            raise Exception('Notification processing failed')

        # Track processed events for verification
        self.processed_events.append({'event_type': event_type, 'task_data': task_data})


@pytest.fixture
def fake_notification_service():
    """Create fake notification service and inject it into handler."""
    fake_service = FakeNotificationService()

    # Inject fake service into handler module
    import services.notification_service.handler as handler

    original_service = handler.notification_service
    handler.notification_service = fake_service

    yield fake_service

    # Restore original service
    handler.notification_service = original_service
