"""Task entity models and validation."""

import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class TaskStatus(str, Enum):
    """Task status enumeration."""

    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'


class TaskPriority(str, Enum):
    """Task priority enumeration."""

    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'


class Task(BaseModel):
    """Task entity with validation."""

    task_id: str = Field(default_factory=lambda: str(uuid4()), description='Unique task identifier')
    title: str = Field(..., min_length=1, max_length=100, description='Task title')
    description: Optional[str] = Field(None, max_length=500, description='Task description')
    status: TaskStatus = Field(default=TaskStatus.PENDING, description='Task status')
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description='Task priority')
    dependencies: list[str] = Field(default_factory=list, description='List of task IDs this task depends on')
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description='Creation timestamp')
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description='Last update timestamp')
    version: int = Field(default=1, description='Version for optimistic locking')

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean description."""
        if v is not None:
            return v.strip() if v.strip() else None
        return v

    def model_post_init(self, __context) -> None:
        """Post-initialization to ensure updated_at is set."""
        if self.updated_at == self.created_at and hasattr(self, '_updating'):
            self.updated_at = datetime.now(UTC)


class TaskEventType(str, Enum):
    """Task event types for EventBridge."""

    TASK_CREATED = 'TaskCreated'
    TASK_UPDATED = 'TaskUpdated'
    TASK_DELETED = 'TaskDeleted'


@dataclass
class TaskEvent:
    """Base class for all task events."""

    event_type: str
    task_data: Dict[str, Any]
    source: str = 'cns427-task-api'
    detail_type_prefix: str = ''

    def __init__(self, event_type: str, task_data: Dict[str, Any], source: str = None, detail_type_prefix: str = None):
        self.event_type = event_type
        self.task_data = task_data
        if source is not None:
            self.source = source
        if detail_type_prefix is not None:
            self.detail_type_prefix = detail_type_prefix

    def to_eventbridge_entry(self, event_bus_name: str = None) -> Dict[str, Any]:
        """Convert to EventBridge entry format."""
        detail_type = f'{self.detail_type_prefix}{self.event_type}' if self.detail_type_prefix else self.event_type
        bus_name = event_bus_name or os.environ.get('EVENT_BUS_NAME', 'TaskEvents')

        return {
            'Source': self.source,
            'DetailType': detail_type,
            'Detail': json.dumps(self.task_data, default=str),  # default=str handles datetime serialization
            'EventBusName': bus_name,
        }

    @classmethod
    def from_eventbridge_event(cls, event: Dict[str, Any]) -> 'TaskEvent':
        """
        Create TaskEvent from EventBridge event structure.

        Args:
            event: EventBridge event with structure:
                {
                    "version": "0",
                    "detail-type": "TaskCreated",
                    "source": "cns427-task-api",
                    "detail": { task_data }
                }

        Returns:
            TaskEvent instance
        """
        detail_type = event.get('detail-type', '')
        source = event.get('source', 'cns427-task-api')
        detail = event.get('detail', {})

        # Remove TEST- prefix if present
        event_type = detail_type.replace('TEST-', '')

        return cls(event_type=event_type, task_data=detail, source=source)


@dataclass
class TaskCreatedEvent(TaskEvent):
    """Task created event."""

    def __init__(self, task: Task, source: str = None, detail_type_prefix: str = None):
        # Convert Task to dict
        task_dict = task.model_dump(mode='json')
        # Convert datetime objects to ISO format strings
        task_dict['created_at'] = task.created_at.isoformat()
        task_dict['updated_at'] = task.updated_at.isoformat()

        super().__init__('TaskCreated', task_dict, source=source, detail_type_prefix=detail_type_prefix)


@dataclass
class TaskUpdatedEvent(TaskEvent):
    """Task updated event."""

    def __init__(self, task: Task, source: str = None, detail_type_prefix: str = None):
        # Convert Task to dict
        task_dict = task.model_dump(mode='json')
        # Convert datetime objects to ISO format strings
        task_dict['created_at'] = task.created_at.isoformat()
        task_dict['updated_at'] = task.updated_at.isoformat()

        super().__init__('TaskUpdated', task_dict, source=source, detail_type_prefix=detail_type_prefix)


@dataclass
class TaskDeletedEvent(TaskEvent):
    """Task deleted event."""

    def __init__(self, task_id: str, source: str = None, detail_type_prefix: str = None):
        super().__init__('TaskDeleted', {'task_id': task_id}, source=source, detail_type_prefix=detail_type_prefix)
