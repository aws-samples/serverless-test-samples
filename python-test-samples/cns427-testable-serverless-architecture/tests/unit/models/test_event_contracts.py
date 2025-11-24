"""
Event Contract Tests using Pydantic

Demonstrates 4 key contract testing concepts:
1. Schema validation - Event structure compliance using Pydantic
2. Consumer contracts - Consumer-specific field requirements
3. Rule patterns - EventBridge routing validation
4. Drift detection - Checks breaking schema changes are caught
"""

import json
from typing import List, Literal

from pydantic import BaseModel, ValidationError

from services.task_service.models.task import Task, TaskCreatedEvent, TaskDeletedEvent, TaskUpdatedEvent


# Pydantic Contract Schemas
class TaskDetailSchema(BaseModel):
    """Contract schema for TaskCreated/TaskUpdated events."""

    task_id: str
    title: str
    description: str | None
    status: Literal['pending', 'in_progress', 'completed']
    priority: Literal['low', 'medium', 'high']
    dependencies: List[str]
    created_at: str
    updated_at: str
    version: int


class TaskDeletedDetailSchema(BaseModel):
    """Contract schema for TaskDeleted events."""

    task_id: str


class EventBridgeEnvelopeSchema(BaseModel):
    """Contract schema for EventBridge envelope."""

    Source: Literal['cns427-task-api']
    DetailType: Literal['TaskCreated', 'TaskUpdated', 'TaskDeleted']
    Detail: str  # JSON string
    EventBusName: str


# Validation Functions
def validate_against_contract(event: dict, message_name: str) -> List[str]:
    """Validate event against Pydantic contract schemas."""
    errors = []

    try:
        # Validate EventBridge envelope
        EventBridgeEnvelopeSchema.model_validate(event)

        # Parse and validate Detail content
        detail = json.loads(event['Detail'])

        if message_name in ['TaskCreated', 'TaskUpdated']:
            TaskDetailSchema.model_validate(detail)
        elif message_name == 'TaskDeleted':
            TaskDeletedDetailSchema.model_validate(detail)
        else:
            errors.append(f'Unknown message type: {message_name}')

    except ValidationError as e:
        for error in e.errors():
            field_path = ' -> '.join(str(loc) for loc in error['loc'])
            errors.append(f'Validation failed at {field_path}: {error["msg"]}')
    except json.JSONDecodeError:
        errors.append('Detail field is not valid JSON')
    except Exception as e:
        errors.append(f'Validation error: {str(e)}')

    return errors


class TestEventContracts:
    """
    Event contract tests using Pydantic validation.

    Pydantic automatically validates:
        - String fields are strings
        - Status is one of the allowed literals
        - Priority is one of the allowed literals
        - Dependencies is a list of strings
        - All required fields are present
    """

    def test_schema_validation(self):
        """1. Schema Validation - Event structure compliance using Pydantic."""
        # GIVEN a task created through domain logic
        task = Task(title='Sync Test', description='Testing schema sync')

        # WHEN creating event using Event model
        created_event_model = TaskCreatedEvent(task)
        created_event = created_event_model.to_eventbridge_entry()

        # THEN event should pass Pydantic validation
        errors = validate_against_contract(created_event, 'TaskCreated')
        assert errors == [], f'TaskCreated schema out of sync: {errors}'

        # AND should have correct EventBridge structure
        assert created_event['Source'] == 'cns427-task-api'
        assert created_event['DetailType'] == 'TaskCreated'

        # AND detail should have required fields with correct types
        detail = json.loads(created_event['Detail'])
        required_fields = ['task_id', 'title', 'status', 'priority', 'version']

        for field in required_fields:
            assert field in detail, f'Missing required field: {field}'
            assert detail[field] is not None, f'Field {field} cannot be null'

    def test_consumer_contract_notification_service(self):
        """2. Consumer Contract - Notification service requirements."""
        # GIVEN notification service needs: task_id, title, status
        task = Task(title='Notification Test', description='Demo')

        # WHEN creating event using Event model
        event_model = TaskCreatedEvent(task)
        event = event_model.to_eventbridge_entry()

        # THEN notification service required fields should be present
        detail = json.loads(event['Detail'])
        notification_fields = ['task_id', 'title', 'status']
        for field in notification_fields:
            assert field in detail, f'Notification service requires: {field}'
            assert isinstance(detail[field], str), f'Field {field} must be string for notifications'

    def test_eventbridge_rule_pattern_matching(self):
        """3. Rule Pattern - EventBridge routing validation."""
        # GIVEN EventBridge rule pattern for notification service
        rule_pattern = {'source': ['cns427-task-api'], 'detail-type': ['TaskCreated', 'TaskUpdated', 'TaskDeleted']}

        # WHEN creating different event types using Event models
        task = Task(title='Rule Pattern Test')
        test_cases = [TaskCreatedEvent(task), TaskUpdatedEvent(task), TaskDeletedEvent('task-123')]

        for event_model in test_cases:
            event = event_model.to_eventbridge_entry()

            # THEN event should match rule pattern
            assert event['Source'] in rule_pattern['source'], f'Source mismatch for {event_model.event_type}'
            assert event['DetailType'] in rule_pattern['detail-type'], f'DetailType mismatch for {event_model.event_type}'

    def test_contract_violation_detection(self):
        """4. Schema drift detection: Pydantic catches contract violations immediately."""
        # GIVEN changes to domain logic
        # WHEN publishing events with new schema
        invalid_events = [
            # Missing required fields
            {
                'Source': 'cns427-task-api',
                'DetailType': 'TaskCreated',
                'Detail': json.dumps({'task_id': 'task-123', 'title': 'Invalid'}),
                'EventBusName': 'test',
            },
            # Wrong field types
            {
                'Source': 'cns427-task-api',
                'DetailType': 'TaskCreated',
                'Detail': json.dumps(
                    {
                        'task_id': 'task-123',
                        'title': 'Invalid',
                        'status': 'invalid_status',  # Not in allowed literals
                        'priority': 'urgent',  # Not in allowed literals
                        'dependencies': 'not_a_list',  # Wrong type
                        'created_at': '2023-01-01',
                        'updated_at': '2023-01-01',
                        'version': 123,
                    }
                ),
                'EventBusName': 'test',
            },
        ]

        # THEN Pydantic should catch all violations
        for invalid_event in invalid_events:
            errors = validate_against_contract(invalid_event, 'TaskCreated')
            assert len(errors) > 0, 'Should detect contract violations'
