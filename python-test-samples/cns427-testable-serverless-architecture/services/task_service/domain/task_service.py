"""Domain logic for task management operations."""

from datetime import UTC, datetime
from typing import List, Optional, Tuple
from uuid import uuid4

from aws_lambda_powertools import Logger

from services.task_service.domain.business_rules import can_transition_to, has_circular_dependency
from services.task_service.domain.exceptions import CircularDependencyError, ConflictError
from services.task_service.models.api import CreateTaskRequest, UpdateTaskRequest
from services.task_service.models.task import Task, TaskStatus
from shared.integration.interfaces import EventPublisher, TaskRepository

# Initialize logger at module level - will include module name in logs
logger = Logger()


class TaskService:
    """Pure business logic for task operations."""

    def __init__(self, repository: TaskRepository = None, event_publisher: EventPublisher = None):
        """Initialize service with dependencies."""
        if repository is None or event_publisher is None:
            import os

            from shared.integration.dynamodb_adapter import DynamoDBTaskRepository
            from shared.integration.eventbridge_adapter import EventBridgePublisher

            self.repository = repository or DynamoDBTaskRepository(table_name=os.environ.get('TASKS_TABLE_NAME', 'tasks'))
            self.event_publisher = event_publisher or EventBridgePublisher(event_bus_name=os.environ.get('EVENT_BUS_NAME', 'TaskEvents'))
        else:
            self.repository = repository
            self.event_publisher = event_publisher

    def create_task(self, request: CreateTaskRequest) -> Task:
        """Create a new task from request data."""
        # Generate task ID and timestamp for version
        task_id = str(uuid4())
        now = datetime.now(UTC)
        version = int(now.timestamp() * 1000)  # UTC timestamp in milliseconds

        logger.info(f'Creating task with ID: {task_id}')

        # Validate dependencies for circular references
        if request.dependencies:
            logger.debug(f'Validating dependencies: {request.dependencies}')
            self._validate_dependencies(task_id, request.dependencies)

        # Create task entity
        task = Task(
            task_id=task_id,
            title=request.title,
            description=request.description,
            priority=request.priority,
            dependencies=request.dependencies,
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
            version=version,
        )

        # Persist task
        created_task = self.repository.create_task(task)

        # Publish event
        from services.task_service.models.task import TaskCreatedEvent

        event = TaskCreatedEvent(created_task)
        self.event_publisher.publish_event(event)

        logger.info(f'Task created successfully: {task_id}')
        return created_task

    def get_task(self, task_id: str) -> Task:
        """Retrieve a task by ID."""
        task = self.repository.get_task(task_id)
        if task is None:
            raise ValueError(f'Task not found: {task_id}')
        return task

    def list_tasks(self, limit: Optional[int] = None, next_token: Optional[str] = None) -> Tuple[List[Task], Optional[str]]:
        """List tasks with pagination."""
        validated_limit = self._validate_pagination_params(limit)
        return self.repository.list_tasks(validated_limit, next_token)

    def update_task(self, task_id: str, request: UpdateTaskRequest) -> Task:
        """Update an existing task with optimistic concurrency control."""
        logger.info(f'Updating task: {task_id}, request_version: {request.version}')

        # Get existing task
        existing_task = self.repository.get_task(task_id)
        if existing_task is None:
            raise ValueError(f'Task not found: {task_id}')

        logger.debug(f'Existing task version: {existing_task.version}, Request version: {request.version}')

        # Validate version for optimistic locking
        if existing_task.version != request.version:
            # Conflict detected - version mismatch
            logger.debug(f'Version mismatch! Existing: {existing_task.version}, Request: {request.version}')
            raise ConflictError(f'Task {task_id} was modified by another process', current_task=existing_task.model_dump())

        # Validate dependencies if being updated
        if request.dependencies is not None:
            self._validate_dependencies(task_id, request.dependencies)

        # Validate status transition if status is being updated
        if request.status is not None:
            new_status = TaskStatus(request.status)
            if not can_transition_to(existing_task.status, new_status):
                raise ValueError(f'Invalid status transition from {existing_task.status.value} to {new_status.value}')

        # Create updated task with new values
        # Domain logic: Generate new version
        now = datetime.now(UTC)
        new_version = int(now.timestamp() * 1000)  # UTC timestamp in milliseconds

        # Keep track of old version for optimistic locking
        old_version = existing_task.version

        logger.debug(f'Generating new version: {new_version} (old: {old_version})')

        updated_data = existing_task.model_dump()
        updated_data['updated_at'] = now
        updated_data['version'] = new_version

        if request.title is not None:
            updated_data['title'] = request.title
        if request.description is not None:
            updated_data['description'] = request.description
        if request.status is not None:
            updated_data['status'] = TaskStatus(request.status)
            logger.debug(f'Updating status to: {request.status}')
        if request.priority is not None:
            updated_data['priority'] = request.priority
        if request.dependencies is not None:
            updated_data['dependencies'] = request.dependencies

        updated_task = Task(**updated_data)

        logger.debug(f'Calling repository.update_task with expected_version={old_version}, new_version={new_version}')

        # Persist updated task with old version for conditional check
        saved_task = self.repository.update_task(updated_task, expected_version=old_version)

        logger.debug(f'Repository update successful, saved version: {saved_task.version}')

        # Publish event
        from services.task_service.models.task import TaskUpdatedEvent

        event = TaskUpdatedEvent(saved_task)
        self.event_publisher.publish_event(event)

        return saved_task

    def delete_task(self, task_id: str) -> None:
        """Delete a task."""
        # Get task to validate existence and get version
        existing_task = self.repository.get_task(task_id)
        if existing_task is None:
            raise ValueError(f'Task not found: {task_id}')

        # Delete task
        self.repository.delete_task(task_id, existing_task.version)

        # Publish event
        from services.task_service.models.task import TaskDeletedEvent

        event = TaskDeletedEvent(task_id)
        self.event_publisher.publish_event(event)

    def _validate_dependencies(self, task_id: str, dependencies: list[str]) -> None:
        """Validate task dependencies for circular references."""
        if not dependencies:
            return

        # Get all dependencies from repository
        all_dependencies = self._get_all_dependencies()

        for dep_id in dependencies:
            if has_circular_dependency(task_id, dep_id, all_dependencies):
                raise CircularDependencyError(f'Circular dependency detected with task {dep_id}')

    def _get_all_dependencies(self) -> dict[str, list[str]]:
        """Get all task dependencies from repository."""
        tasks, _ = self.repository.list_tasks(limit=1000)
        dependencies = {}
        for task in tasks:
            if task.dependencies:
                dependencies[task.task_id] = task.dependencies
        return dependencies

    def _validate_pagination_params(self, limit: Optional[int] = None) -> int:
        """Validate and normalize pagination parameters."""
        if limit is None:
            return 50
        if limit < 1:
            raise ValueError('Limit must be greater than 0')
        if limit > 100:
            raise ValueError('Limit cannot exceed 100')
        return limit
