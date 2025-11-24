"""Business rules for task management."""

from typing import Dict, List

from services.task_service.models.task import TaskStatus


def is_valid_version_token(version_token: str) -> bool:
    """
    Business Rule: Version token format validation.

    Rules:
    - Version tokens must be non-empty strings
    - Version tokens should be numeric (timestamp milliseconds)
    - Version tokens must be positive integers when converted
    """
    if not version_token or not isinstance(version_token, str):
        return False

    try:
        # Version tokens are timestamp milliseconds, so should be positive integers
        timestamp = int(version_token)
        return timestamp > 0
    except ValueError:
        return False


def compare_version_tokens(token1: str, token2: str) -> int:
    """
    Business Rule: Version token comparison for conflict detection.

    Returns:
    - -1 if token1 is older than token2
    - 0 if tokens are equal
    - 1 if token1 is newer than token2

    Raises ValueError if tokens are invalid.
    """
    if not is_valid_version_token(token1) or not is_valid_version_token(token2):
        raise ValueError('Invalid version token format')

    timestamp1 = int(token1)
    timestamp2 = int(token2)

    if timestamp1 < timestamp2:
        return -1
    elif timestamp1 > timestamp2:
        return 1
    else:
        return 0


def validate_version_token_for_update(version_token: str) -> None:
    """
    Business Rule: Version token validation for update operations.

    Rules:
    - Version token is required for all update operations
    - Version token must be in valid format
    """
    if not version_token:
        raise ValueError('version_token is required for update operations')

    if not is_valid_version_token(version_token):
        raise ValueError('Invalid version_token format. Must be a positive integer string.')


def can_transition_to(current_status: TaskStatus, new_status: TaskStatus) -> bool:
    """
    Business Rule: Tasks can only transition through valid states.

    Valid transitions:
    - pending -> in_progress -> completed
    - pending -> completed (skip in_progress for simple tasks)
    - completed -> pending (reopen task)
    - NOT allowed: in_progress -> pending (can't go backwards without completing)
    """
    valid_transitions = {
        TaskStatus.PENDING: [TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED],
        TaskStatus.IN_PROGRESS: [TaskStatus.COMPLETED],
        TaskStatus.COMPLETED: [TaskStatus.PENDING],  # Reopen task
    }
    return new_status in valid_transitions.get(current_status, [])


def has_circular_dependency(task_id: str, dependency_id: str, all_dependencies: Dict[str, List[str]]) -> bool:
    """
    Business Rule: Prevent circular dependencies.

    Rules:
    - Adding a dependency should not create a cycle
    - Use depth-first search to detect cycles
    """
    if task_id == dependency_id:
        return True  # Self-dependency is circular

    visited = set()

    def check_cycle(current_id: str) -> bool:
        if current_id in visited:
            return True
        visited.add(current_id)

        for dep_id in all_dependencies.get(current_id, []):
            if dep_id == task_id:  # Would create cycle back to original task
                return True
            if check_cycle(dep_id):
                return True

        visited.remove(current_id)
        return False

    return check_cycle(dependency_id)
