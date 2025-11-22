"""Unit tests for task service business logic.

Focus: Test actual business rules and behavior, not pass-through operations.
- Version conflict detection
- Circular dependency validation
- Status transition validation
- Pagination validation
- Error handling
- Repository/publisher interaction patterns
"""

from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from services.task_service.domain.exceptions import CircularDependencyError, ConflictError
from services.task_service.domain.task_service import TaskService
from services.task_service.models.api import CreateTaskRequest, UpdateTaskRequest
from services.task_service.models.task import Task, TaskEventType, TaskPriority, TaskStatus


class TestTaskService:
    """Unit tests for task service business logic."""

    @pytest.fixture
    def repository(self):
        """Create mock repository for each test."""
        return Mock()

    @pytest.fixture
    def publisher(self):
        """Create mock publisher for each test."""
        return Mock()

    @pytest.fixture
    def service(self, repository, publisher):
        """Create task service with mocks."""
        return TaskService(repository, publisher)

    def test_create_task_calls_repository_and_publisher(self, service, repository, publisher):
        """Test that create_task calls repository and publisher correctly."""
        # GIVEN a task creation request
        request = CreateTaskRequest(title='Test Task', priority=TaskPriority.HIGH)

        # Mock repository to return a proper Task object
        now = datetime.now(UTC)
        created_task = Task(
            task_id='test-id',
            title='Test Task',
            priority=TaskPriority.HIGH,
            status=TaskStatus.PENDING,
            dependencies=[],
            created_at=now,
            updated_at=now,
            version=int(now.timestamp() * 1000),
        )
        repository.create_task.return_value = created_task

        # WHEN creating the task
        service.create_task(request)

        # THEN repository should be called with a Task object
        repository.create_task.assert_called_once()
        passed_task = repository.create_task.call_args[0][0]
        assert isinstance(passed_task, Task)
        assert passed_task.title == 'Test Task'
        assert passed_task.priority == TaskPriority.HIGH
        assert passed_task.status == TaskStatus.PENDING

        # AND event should be published
        publisher.publish_event.assert_called_once()
        published_event = publisher.publish_event.call_args[0][0]
        assert published_event.event_type == TaskEventType.TASK_CREATED

    def test_update_task_calls_repository_and_publisher(self, service, repository, publisher):
        """Test that update_task calls repository and publisher correctly."""
        # GIVEN existing task
        now = datetime.now(UTC)
        int(now.timestamp() * 1000)
        existing_task = Task(
            task_id='test-id',
            title='Original',
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            dependencies=[],
            created_at=now,
            updated_at=now,
            version=int(now.timestamp() * 1000),
        )
        repository.get_task.return_value = existing_task

        # Mock update to return a proper Task object
        updated_task = Task(
            task_id='test-id',
            title='Updated',
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            dependencies=[],
            created_at=now,
            updated_at=datetime.now(UTC),
            version=int(datetime.now(UTC).timestamp() * 1000),
        )
        repository.update_task.return_value = updated_task

        # WHEN updating task
        update_request = UpdateTaskRequest(title='Updated', version=existing_task.version)
        service.update_task('test-id', update_request)

        # THEN repository should be called
        repository.get_task.assert_called_once_with('test-id')
        repository.update_task.assert_called_once()

        # AND update event should be published
        publisher.publish_event.assert_called_once()
        update_event = publisher.publish_event.call_args[0][0]
        assert update_event.event_type == TaskEventType.TASK_UPDATED

    def test_update_task_version_mismatch_raises_conflict_error(self, service, repository):
        """BUSINESS RULE: Version mismatch should raise ConflictError."""
        # GIVEN existing task with specific version
        now = datetime.now(UTC)
        existing_task = Task(
            task_id='test-id',
            title='Test',
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            dependencies=[],
            created_at=now,
            updated_at=now,
            version=int(now.timestamp() * 1000),
        )
        repository.get_task.return_value = existing_task

        # WHEN attempting to update with wrong version
        update_request = UpdateTaskRequest(title='Updated', version=999)  # Wrong version

        # THEN should raise ConflictError
        with pytest.raises(ConflictError) as exc_info:
            service.update_task('test-id', update_request)

        assert 'modified by another process' in str(exc_info.value).lower()
        # Repository update should NOT be called
        repository.update_task.assert_not_called()

    def test_update_task_invalid_status_transition_raises_error(self, service, repository):
        """BUSINESS RULE: Invalid status transitions should be rejected."""
        # GIVEN task in COMPLETED status
        now = datetime.now(UTC)
        existing_task = Task(
            task_id='test-id',
            title='Test',
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.MEDIUM,
            dependencies=[],
            created_at=now,
            updated_at=now,
            version=int(now.timestamp() * 1000),
        )
        repository.get_task.return_value = existing_task

        # WHEN attempting invalid transition (COMPLETED -> IN_PROGRESS not allowed)
        update_request = UpdateTaskRequest(status='in_progress', version=existing_task.version)

        # THEN should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            service.update_task('test-id', update_request)

        assert 'invalid status transition' in str(exc_info.value).lower()
        # Repository update should NOT be called
        repository.update_task.assert_not_called()

    def test_update_task_with_circular_dependency_raises_error(self, service, repository):
        """BUSINESS RULE: Circular dependencies should be detected."""
        # GIVEN existing task
        now = datetime.now(UTC)
        existing_task = Task(
            task_id='test-id',
            title='Test',
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            dependencies=[],
            created_at=now,
            updated_at=now,
            version=int(now.timestamp() * 1000),
        )
        repository.get_task.return_value = existing_task

        # Mock repository to return tasks that would create circular dependency
        repository.list_tasks.return_value = ([Mock(task_id='dep-1', dependencies=['test-id'])], None)

        # WHEN attempting to add dependency that creates cycle
        update_request = UpdateTaskRequest(dependencies=['dep-1'], version=existing_task.version)

        # THEN should raise CircularDependencyError
        with pytest.raises(CircularDependencyError):
            service.update_task('test-id', update_request)

        # Repository update should NOT be called
        repository.update_task.assert_not_called()

    def test_get_task_not_found_raises_error(self, service, repository):
        """BUSINESS RULE: Getting non-existent task should raise ValueError."""
        # GIVEN repository returns None for non-existent task
        repository.get_task.return_value = None

        # WHEN getting non-existent task
        # THEN should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            service.get_task('non-existent-id')

        assert 'not found' in str(exc_info.value).lower()
        repository.get_task.assert_called_once_with('non-existent-id')

    def test_delete_task_calls_repository_and_publisher(self, service, repository, publisher):
        """Test that delete_task calls repository and publisher correctly."""
        # GIVEN existing task
        now = datetime.now(UTC)
        existing_task = Task(
            task_id='test-id',
            title='Task to Delete',
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            dependencies=[],
            created_at=now,
            updated_at=now,
            version=int(now.timestamp() * 1000),
        )
        repository.get_task.return_value = existing_task

        # WHEN deleting task
        service.delete_task('test-id')

        # THEN repository delete should be called with version
        repository.get_task.assert_called_once_with('test-id')
        repository.delete_task.assert_called_once_with('test-id', existing_task.version)

        # AND delete event should be published
        publisher.publish_event.assert_called_once()
        delete_event = publisher.publish_event.call_args[0][0]
        assert delete_event.event_type == TaskEventType.TASK_DELETED

    def test_delete_task_not_found_raises_error(self, service, repository):
        """BUSINESS RULE: Deleting non-existent task should raise ValueError."""
        # GIVEN repository returns None for non-existent task
        repository.get_task.return_value = None

        # WHEN deleting non-existent task
        # THEN should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            service.delete_task('non-existent-id')

        assert 'not found' in str(exc_info.value).lower()
        # Repository delete should NOT be called
        repository.delete_task.assert_not_called()

    def test_validate_pagination_params_default(self, service):
        """Test default pagination parameters."""
        result = service._validate_pagination_params(None)
        assert result == 50

    def test_validate_pagination_params_valid(self, service):
        """Test valid pagination parameters."""
        result = service._validate_pagination_params(25)
        assert result == 25

    def test_validate_pagination_params_too_small(self, service):
        """Test pagination limit too small raises error."""
        with pytest.raises(ValueError):
            service._validate_pagination_params(0)

    def test_validate_pagination_params_too_large(self, service):
        """Test pagination limit too large raises error."""
        with pytest.raises(ValueError):
            service._validate_pagination_params(101)
