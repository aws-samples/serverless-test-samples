"""API request and response models."""

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from services.task_service.models.task import Task, TaskPriority


class CreateTaskRequest(BaseModel):
    """Request model for creating a new task."""

    title: str = Field(..., min_length=1, max_length=100, description='Task title')

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not just whitespace."""
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip()

    description: Optional[str] = Field(None, max_length=500, description='Task description')
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description='Task priority')
    dependencies: list[str] = Field(default_factory=list, description='List of task IDs this task depends on')


class UpdateTaskRequest(BaseModel):
    """Request model for updating an existing task."""

    title: Optional[str] = Field(None, min_length=1, max_length=100, description='Task title')

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate title is not just whitespace."""
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip() if v else v

    description: Optional[str] = Field(None, max_length=500, description='Task description')
    status: Optional[str] = Field(None, description='Task status')

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate status is a valid TaskStatus value."""
        if v is not None:
            from services.task_service.models.task import TaskStatus

            valid_statuses = [status.value for status in TaskStatus]
            if v not in valid_statuses:
                raise ValueError(f'Invalid status. Must be one of: {valid_statuses}')
        return v

    priority: Optional[TaskPriority] = Field(None, description='Task priority')
    dependencies: Optional[list[str]] = Field(None, description='List of task IDs this task depends on')
    version: int = Field(..., description='Current version for optimistic locking')


class TaskResponse(BaseModel):
    """Response model for task operations."""

    task_id: str = Field(..., description='Unique task identifier')
    title: str = Field(..., description='Task title')
    description: Optional[str] = Field(None, description='Task description')
    status: str = Field(..., description='Task status')
    priority: str = Field(..., description='Task priority')
    dependencies: list[str] = Field(default_factory=list, description='List of task IDs this task depends on')
    created_at: str = Field(..., description='Creation timestamp (ISO 8601)')
    updated_at: str = Field(..., description='Last update timestamp (ISO 8601)')
    version: int = Field(..., description='Current version')

    @classmethod
    def from_task(cls, task: Task) -> 'TaskResponse':
        """Create TaskResponse from Task entity."""
        return cls(
            task_id=task.task_id,
            title=task.title,
            description=task.description,
            status=task.status.value,
            priority=task.priority.value,
            dependencies=task.dependencies,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat(),
            version=task.version,
        )


class PaginationInfo(BaseModel):
    """Pagination information for list responses."""

    next_token: Optional[str] = Field(None, description='Token for next page')
    limit: int = Field(..., description='Number of items per page')


class ListTasksResponse(BaseModel):
    """Response model for listing tasks."""

    tasks: List[TaskResponse] = Field(..., description='List of tasks')
    pagination: PaginationInfo = Field(..., description='Pagination information')


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str = Field(..., description='Error type')
    message: str = Field(..., description='Error message')
    details: Optional[dict] = Field(None, description='Additional error details')
