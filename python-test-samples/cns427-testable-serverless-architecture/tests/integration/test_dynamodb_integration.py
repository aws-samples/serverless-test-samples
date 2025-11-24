"""
DynamoDB Integration Tests - Real AWS DynamoDB

Tests TaskRepository against actual DynamoDB table.
Focuses on create task flow with real data persistence.
"""

import json
import os
import time
import uuid
from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

# Set table name for integration tests from config
from infrastructure.config import InfrastructureConfig
from services.task_service.domain.exceptions import ConflictError
from services.task_service.domain.task_service import TaskService
from services.task_service.models.task import Task, TaskPriority, TaskStatus
from shared.integration.dynamodb_adapter import DynamoDBTaskRepository
from tests.integration.fakes.dynamodb_fake import DynamoDBFake
from tests.unit.test_helpers import create_api_gateway_event, create_test_context

config = InfrastructureConfig()
os.environ['TASKS_TABLE_NAME'] = config.tasks_table_name()


@pytest.fixture
def task_repository():
    """Create TaskRepository instance for testing."""
    return DynamoDBTaskRepository(table_name=os.environ['TASKS_TABLE_NAME'])


@pytest.fixture
def test_task_id():
    """Generate unique task ID for testing."""
    return f'test-{uuid.uuid4()}'


@pytest.fixture
def cleanup_task(task_repository):
    """Cleanup fixture to delete test tasks after each test."""
    task_ids = []

    def register(task_id):
        task_ids.append(task_id)

    yield register

    # Cleanup after test
    for task_id in task_ids:
        try:
            # Get the task to retrieve its current version
            task = task_repository.get_task(task_id)
            if task:
                task_repository.delete_task(task_id, task.version)
            else:
                print(f'[Cleanup] Task {task_id} not found, skipping delete')
        except Exception as e:
            # Log warning but don't fail the test
            print(f'[Cleanup] Warning: Failed to delete task {task_id}: {e}')
            # Continue with other cleanups


@pytest.fixture
def mock_event_publisher():
    """Create a mock event publisher for testing."""
    return Mock()


@pytest.fixture
def fake_task_service_with_error(request):
    """Fixture to create TaskService with fake DynamoDB for error simulation."""
    error_type = request.param if hasattr(request, 'param') else 'throttling'

    # Create fake DynamoDB client with error simulation
    fake_dynamodb = DynamoDBFake(error_type=error_type)

    # Create real repository but inject fake DynamoDB client
    fake_repo = DynamoDBTaskRepository(table_name=os.environ['TASKS_TABLE_NAME'])
    fake_repo.dynamodb = fake_dynamodb

    # Create service with fake repo and mock publisher
    mock_publisher = Mock()
    fake_service = TaskService(fake_repo, mock_publisher)

    # Inject fake service into handler module
    import services.task_service.handler as handler_module

    handler_module.task_service = fake_service

    yield fake_service


class TestDynamoDBIntegration:
    """Test TaskRepository with real DynamoDB."""

    def test_create_and_retrieve_task(self, task_repository, test_task_id, cleanup_task):
        """Test creating and retrieving a task from real DynamoDB."""
        # GIVEN a new task
        now = datetime.now(UTC)
        task = Task(
            task_id=test_task_id,
            title='Integration Test Task',
            description='Testing real DynamoDB',
            dependencies=[],
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            created_at=now,
            updated_at=now,
            version=int(now.timestamp() * 1000),
        )
        cleanup_task(test_task_id)

        # WHEN saving to DynamoDB
        task_repository.create_task(task)

        # THEN should be able to retrieve it
        retrieved = task_repository.get_task(test_task_id)
        assert retrieved is not None
        assert retrieved.task_id == test_task_id
        assert retrieved.title == 'Integration Test Task'
        assert retrieved.description == 'Testing real DynamoDB'

    def test_create_task_with_dependencies(self, task_repository, cleanup_task):
        """Test creating task with dependencies."""
        # GIVEN two tasks with dependency relationship
        task1_id = f'test-{uuid.uuid4()}'
        task2_id = f'test-{uuid.uuid4()}'
        cleanup_task(task1_id)
        cleanup_task(task2_id)

        now = datetime.now(UTC)
        task1 = Task(
            task_id=task1_id,
            title='Task 1',
            dependencies=[],
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            created_at=now,
            updated_at=now,
            version=int(now.timestamp() * 1000),
        )

        task2 = Task(
            task_id=task2_id,
            title='Task 2',
            dependencies=[task1_id],
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            created_at=now,
            updated_at=now,
            version=int(now.timestamp() * 1000),
        )

        # WHEN saving both tasks
        task_repository.create_task(task1)
        task_repository.create_task(task2)

        # THEN should retrieve task with dependencies
        retrieved = task_repository.get_task(task2_id)
        assert retrieved is not None
        assert retrieved.dependencies == [task1_id]

    def test_conditional_update(self, task_repository, test_task_id, cleanup_task):
        """Test conflict resolution with real DynamoDB conditional updates."""

        # GIVEN a task in real DynamoDB
        now = datetime.now(UTC)
        task = Task(
            task_id=test_task_id,
            title='Conflict Resolution Test',
            description='Testing real DynamoDB conditional updates',
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            dependencies=[],
            created_at=now,
            updated_at=now,
            version=int(now.timestamp() * 1000),
        )
        cleanup_task(test_task_id)

        # Save initial task
        task_repository.create_task(task)
        original_version = task.version

        # WHEN attempting update with correct version
        time.sleep(0.001)  # Ensure different timestamp
        task.title = 'Updated Title'
        # Generate new version (simulating domain service behavior)
        new_version = int(datetime.now(UTC).timestamp() * 1000)
        task.version = new_version
        result = task_repository.update_task(task, expected_version=original_version)

        # THEN update should succeed
        assert result is not None
        assert result.title == 'Updated Title'
        assert result.version == new_version
        assert result.version != original_version

        # WHEN attempting another update with stale version
        task.title = 'Should Fail'
        another_new_version = int(datetime.now(UTC).timestamp() * 1000)
        task.version = another_new_version

        # THEN second update should raise ConflictError (using stale expected_version)
        with pytest.raises(ConflictError) as exc_info:
            task_repository.update_task(task, expected_version=original_version)  # Wrong! Should be new_version

        # AND error should include current task state
        assert exc_info.value.current_task is not None
        assert exc_info.value.current_task['title'] == 'Updated Title'


class TestDynamoDBErrorSimulation:
    """Test error handling with DynamoDB fake through full handler integration."""

    @pytest.mark.parametrize('fake_task_service_with_error', ['throttling'], indirect=True)
    def test_throttling_error_returns_503_with_retry_info(self, fake_task_service_with_error):
        """Test that DynamoDB throttling returns 503 Service Unavailable with retry guidance."""
        # GIVEN a system experiencing DynamoDB throttling (injected via fixture)
        # WHEN client tries to create a task
        event = create_api_gateway_event(method='POST', path='/tasks', body={'title': 'New Task', 'description': 'Test'})

        lambda_context = create_test_context()
        from services.task_service.handler import lambda_handler

        response = lambda_handler(event, lambda_context)

        # THEN should return 503 Service Unavailable
        assert response['statusCode'] == 503, f'Expected 503 but got {response["statusCode"]}'

        # AND response should include retry guidance in message
        body = json.loads(response['body'])
        message = body.get('message', '').lower()
        assert 'retry' in message or 'unavailable' in message or 'capacity' in message, (
            f'Expected retry guidance in message but got: {body.get("message")}'
        )

    @pytest.mark.parametrize('fake_task_service_with_error', ['iam'], indirect=True)
    def test_iam_error_returns_500_internal_error(self, fake_task_service_with_error):
        """Test that IAM/permission errors return 500 Internal Server Error (not exposed to client)."""
        # GIVEN a system with IAM permission issues (injected via fixture)
        # WHEN client tries to create a task
        event = create_api_gateway_event(method='POST', path='/tasks', body={'title': 'New Task', 'description': 'Test'})

        lambda_context = create_test_context()
        from services.task_service.handler import lambda_handler

        response = lambda_handler(event, lambda_context)

        # THEN should return 500 Internal Server Error
        assert response['statusCode'] == 500, f'Expected 500 but got {response["statusCode"]}'

        # AND response should NOT expose IAM/permission details to client
        body = json.loads(response['body'])
        message = body.get('message', '').lower()
        assert 'permission' not in message and 'access' not in message, f'Should not expose permission details to client: {body.get("message")}'
        assert 'internal' in message or 'error' in message, f'Expected generic internal error message but got: {body.get("message")}'

    @pytest.mark.parametrize('fake_task_service_with_error', ['timeout'], indirect=True)
    def test_timeout_error_returns_503_with_retry_info(self, fake_task_service_with_error):
        """Test that timeout errors return 503 with retry guidance."""
        # GIVEN a system experiencing timeouts (injected via fixture)
        # WHEN client tries to create a task
        event = create_api_gateway_event(method='POST', path='/tasks', body={'title': 'New Task', 'description': 'Test'})

        lambda_context = create_test_context()
        from services.task_service.handler import lambda_handler

        response = lambda_handler(event, lambda_context)

        # THEN should return 503 Service Unavailable
        assert response['statusCode'] == 503, f'Expected 503 but got {response["statusCode"]}'

        # AND response should include retry guidance
        body = json.loads(response['body'])
        message = body.get('message', '').lower()
        assert 'retry' in message or 'unavailable' in message or 'timeout' in message, (
            f'Expected retry guidance in message but got: {body.get("message")}'
        )

    @pytest.mark.parametrize('fake_task_service_with_error', ['conditional_check'], indirect=True)
    def test_conditional_check_failure_returns_409_conflict(self, fake_task_service_with_error):
        """Test that conditional check failures return 409 Conflict with refresh guidance."""
        # GIVEN a system with conditional check failures and an existing task
        # Pre-populate the fake DynamoDB with a task
        task_id = 'test-task-123'
        now = datetime.now(UTC)
        fake_task_data = {
            'task_id': task_id,
            'title': 'Original Task',
            'description': 'Test',
            'status': 'pending',
            'priority': 'medium',
            'dependencies': [],
            'created_at': now.isoformat(),
            'updated_at': now.isoformat(),
            'version': int(now.timestamp() * 1000),
        }
        # Access the fake DynamoDB through the repository
        fake_repo = fake_task_service_with_error.repository
        fake_repo.dynamodb.set_task_data(task_id, fake_task_data)

        # WHEN client tries to update the task (will trigger conditional check failure)
        update_event = create_api_gateway_event(
            method='PUT',
            path=f'/tasks/{task_id}',
            body={
                'title': 'Updated Task',
                'version': 1234567890123,  # Valid format but will trigger conditional check failure
            },
        )

        lambda_context = create_test_context()
        from services.task_service.handler import lambda_handler

        response = lambda_handler(update_event, lambda_context)

        # THEN should return 409 Conflict
        assert response['statusCode'] == 409, f'Expected 409 but got {response["statusCode"]}'

        # AND response should indicate resource was updated and suggest refresh
        body = json.loads(response['body'])
        message = body.get('message', '').lower()
        assert 'updated' in message or 'modified' in message or 'refresh' in message or 'process' in message, (
            f'Expected message about stale data/refresh but got: {body.get("message")}'
        )
