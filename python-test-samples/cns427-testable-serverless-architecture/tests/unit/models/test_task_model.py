"""Unit tests for task model validation."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from services.task_service.models.task import Task, TaskCreatedEvent, TaskDeletedEvent, TaskPriority, TaskStatus, TaskUpdatedEvent


class TestTask:
    """Test cases for Task model."""

    def test_create_task_with_minimal_data(self):
        """Test creating a task with only required fields."""
        task = Task(title='Test Task')

        assert task.title == 'Test Task'
        assert task.description is None
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.MEDIUM
        assert task.version == 1
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)
        assert len(task.task_id) == 36  # UUID length

    def test_create_task_with_all_fields(self):
        """Test creating a task with all fields specified."""
        task = Task(title='Complete Task', description='A detailed description', status=TaskStatus.IN_PROGRESS, priority=TaskPriority.HIGH)

        assert task.title == 'Complete Task'
        assert task.description == 'A detailed description'
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.priority == TaskPriority.HIGH

    def test_title_validation_empty_string(self):
        """Test that empty title raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Task(title='')

        assert 'String should have at least 1 character' in str(exc_info.value)

    def test_title_validation_whitespace_only(self):
        """Test that whitespace-only title raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Task(title='   ')

        assert 'Title cannot be empty' in str(exc_info.value)

    def test_title_validation_strips_whitespace(self):
        """Test that title whitespace is stripped."""
        task = Task(title='  Test Task  ')
        assert task.title == 'Test Task'

    def test_title_too_long(self):
        """Test that title exceeding max length raises validation error."""
        long_title = 'x' * 101
        with pytest.raises(ValidationError) as exc_info:
            Task(title=long_title)

        assert 'String should have at most 100 characters' in str(exc_info.value)

    def test_description_validation_strips_whitespace(self):
        """Test that description whitespace is stripped."""
        task = Task(title='Test', description='  Description  ')
        assert task.description == 'Description'

    def test_description_validation_empty_becomes_none(self):
        """Test that empty description becomes None."""
        task = Task(title='Test', description='   ')
        assert task.description is None

    def test_description_too_long(self):
        """Test that description exceeding max length raises validation error."""
        long_description = 'x' * 501
        with pytest.raises(ValidationError) as exc_info:
            Task(title='Test', description=long_description)

        assert 'String should have at most 500 characters' in str(exc_info.value)

    def test_status_enum_validation(self):
        """Test that invalid status raises validation error."""
        with pytest.raises(ValidationError):
            Task(title='Test', status='invalid_status')

    def test_priority_enum_validation(self):
        """Test that invalid priority raises validation error."""
        with pytest.raises(ValidationError):
            Task(title='Test', priority='invalid_priority')

    def test_missing_title(self):
        """Test that missing title raises validation error."""
        with pytest.raises(ValidationError):
            Task()


class TestTaskEvent:
    """Test cases for TaskEvent model."""

    def test_create_task_created_event(self):
        """Test creating a TaskCreated event."""
        task = Task(title='Test Task')
        event = TaskCreatedEvent(task)

        assert event.event_type == 'TaskCreated'
        assert event.task_data['task_id'] == task.task_id
        assert event.task_data['title'] == 'Test Task'
        assert event.source == 'cns427-task-api'
        assert event.detail_type_prefix == ''

    def test_create_task_created_event_with_test_prefix(self):
        """Test creating a TaskCreated event with TEST prefix."""
        task = Task(title='Test Task')
        event = TaskCreatedEvent(task, source='TEST-cns427-task-api', detail_type_prefix='TEST-')

        assert event.event_type == 'TaskCreated'
        assert event.source == 'TEST-cns427-task-api'
        assert event.detail_type_prefix == 'TEST-'

        # Test EventBridge entry format
        entry = event.to_eventbridge_entry()
        assert entry['Source'] == 'TEST-cns427-task-api'
        assert entry['DetailType'] == 'TEST-TaskCreated'

    def test_create_task_updated_event(self):
        """Test creating a TaskUpdated event."""
        task = Task(title='Updated Task')
        event = TaskUpdatedEvent(task)

        assert event.event_type == 'TaskUpdated'
        assert event.task_data['task_id'] == task.task_id
        assert event.source == 'cns427-task-api'

    def test_create_task_deleted_event(self):
        """Test creating a TaskDeleted event with no task data."""
        event = TaskDeletedEvent('test-task-id')

        assert event.event_type == 'TaskDeleted'
        assert event.task_data['task_id'] == 'test-task-id'
        assert event.source == 'cns427-task-api'

    def test_event_to_eventbridge_entry(self):
        """Test converting event to EventBridge entry format."""
        task = Task(title='Test Task')
        event = TaskCreatedEvent(task)

        entry = event.to_eventbridge_entry(event_bus_name='TestBus')

        assert entry['Source'] == 'cns427-task-api'
        assert entry['DetailType'] == 'TaskCreated'
        assert entry['EventBusName'] == 'TestBus'
        assert 'Detail' in entry

        # Verify Detail is valid JSON string
        import json

        detail = json.loads(entry['Detail'])
        assert detail['task_id'] == task.task_id
        assert detail['title'] == 'Test Task'
