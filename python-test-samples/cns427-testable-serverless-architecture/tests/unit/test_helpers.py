"""
Test Helper Functions - Simple utilities for demo
"""

import json
from typing import Any, Dict, Optional


def create_api_gateway_event(
    method: str,
    path: str,
    body: Optional[Dict[str, Any]] = None,
    query_parameters: Optional[Dict[str, str]] = None,
    path_parameters: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Create API Gateway event for testing.

    Simple helper that reduces duplication in tests.
    """
    event = {
        'httpMethod': method,
        'path': path,
        'pathParameters': path_parameters,
        'queryStringParameters': query_parameters or {},
        'body': json.dumps(body) if body else None,
        'headers': {'Content-Type': 'application/json'} if body else {},
        'requestContext': {'requestId': 'test-request-id', 'stage': 'test'},
    }
    return event


def create_test_context():
    """Create a mock Lambda context for testing."""

    class MockContext:
        def __init__(self):
            self.function_name = 'test-function'
            self.function_version = '1'
            self.invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789012:function:test-function'
            self.memory_limit_in_mb = 128
            self.remaining_time_in_millis = lambda: 30000
            self.aws_request_id = 'test-request-id'

    return MockContext()


def create_task_event_detail(
    task_id: str = 'test-task-id',
    title: str = 'Test Task',
    status: str = 'pending',
    priority: str = 'medium',
) -> Dict[str, Any]:
    """Create a task event detail for testing using Task model."""
    from datetime import UTC, datetime

    from services.task_service.models.task import Task, TaskCreatedEvent, TaskPriority, TaskStatus

    # Create a Task model instance
    task = Task(
        task_id=task_id,
        title=title,
        description=None,
        status=TaskStatus(status),
        priority=TaskPriority(priority),
        dependencies=[],
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        version=1,
    )

    # Use TaskCreatedEvent to generate the event data
    event = TaskCreatedEvent(task)

    # Return the task_data from the event (which is already a dict)
    return event.task_data


def create_eventbridge_event(
    detail_type: str = 'TaskCreated',
    task_id: str = 'test-task-id',
    title: str = 'Test Task',
    status: str = 'pending',
    priority: str = 'medium',
) -> Dict[str, Any]:
    """Create a full EventBridge event structure for testing."""
    from datetime import UTC, datetime

    from services.task_service.models.task import Task, TaskCreatedEvent, TaskDeletedEvent, TaskPriority, TaskStatus, TaskUpdatedEvent

    # For TaskDeleted, only need task_id
    if detail_type in ['TaskDeleted', 'TEST-TaskDeleted']:
        event = TaskDeletedEvent(task_id)
        return {'detail-type': detail_type, 'detail': event.task_data}

    # For TaskCreated and TaskUpdated, create full task
    task = Task(
        task_id=task_id,
        title=title,
        description=None,
        status=TaskStatus(status),
        priority=TaskPriority(priority),
        dependencies=[],
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        version=1,
    )

    # Choose the right event type
    if 'Updated' in detail_type:
        event = TaskUpdatedEvent(task)
    else:
        event = TaskCreatedEvent(task)

    return {'detail-type': detail_type, 'detail': event.task_data}
