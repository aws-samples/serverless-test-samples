"""In-memory fake implementation of TaskRepository for all test types."""

from typing import Dict, List, Optional

from task_api.models.interfaces import TaskRepository
from task_api.models.task import Task


class InMemoryTaskRepository(TaskRepository):
    """
    In-memory implementation of TaskRepository for testing.

    This fake stores tasks in memory instead of DynamoDB, making it suitable
    for unit tests that need complete isolation from external dependencies.
    """

    def __init__(self):
        """Initialize with empty task storage."""
        self._tasks: Dict[str, Task] = {}

    def create_task(self, task: Task) -> Task:
        """Create a new task in memory."""
        if task.task_id in self._tasks:
            raise ValueError(f'Task already exists: {task.task_id}')

        self._tasks[task.task_id] = task
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by ID from memory."""
        return self._tasks.get(task_id)

    def list_tasks(self, limit: int = 50, next_token: Optional[str] = None) -> tuple[List[Task], Optional[str]]:
        """List tasks with pagination from memory."""
        tasks = list(self._tasks.values())

        # Simple pagination simulation
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except (ValueError, TypeError):
                start_index = 0

        end_index = start_index + limit
        page_tasks = tasks[start_index:end_index]

        # Generate next token if there are more tasks
        next_page_token = None
        if end_index < len(tasks):
            next_page_token = str(end_index)

        return page_tasks, next_page_token

    def update_task(self, task: Task, expected_version: int) -> Task:
        """Update an existing task with optimistic locking."""
        existing_task = self._tasks.get(task.task_id)
        if existing_task is None:
            raise ValueError(f'Task not found: {task.task_id}')

        # Check version for optimistic locking
        if existing_task.version != expected_version:
            from services.task_service.domain.exceptions import ConflictError

            raise ConflictError(f'Version conflict for task: {task.task_id}', current_task=existing_task.model_dump())

        self._tasks[task.task_id] = task
        return task

    def delete_task(self, task_id: str, version: int) -> None:
        """Delete a task with version check."""
        existing_task = self._tasks.get(task_id)
        if existing_task is None:
            raise ValueError(f'Task not found: {task_id}')

        # Check version for optimistic locking
        if existing_task.version != version:
            raise ValueError(f'Version conflict for task: {task_id}')

        del self._tasks[task_id]

    def clear(self) -> None:
        """Clear all tasks (useful for test cleanup)."""
        self._tasks.clear()

    def count(self) -> int:
        """Get total number of tasks."""
        return len(self._tasks)

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks (useful for test verification)."""
        return list(self._tasks.values())

    def simulate_failure(self, should_fail: bool = True, message: str = 'Simulated repository failure'):
        """Configure the fake to simulate failures for error testing."""
        self.should_fail = should_fail
        self.failure_message = message

    def _check_failure(self):
        """Check if failure should be simulated."""
        if getattr(self, 'should_fail', False):
            raise RuntimeError(getattr(self, 'failure_message', 'Simulated repository failure'))
