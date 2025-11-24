"""Domain exceptions for task management."""

from typing import Dict, Optional


class CircularDependencyError(Exception):
    """Raised when a circular dependency is detected."""

    pass


class ConflictError(Exception):
    """Raised when a task update conflicts with concurrent modifications."""

    def __init__(self, message: str, current_task: Optional[Dict] = None):
        super().__init__(message)
        self.message = message
        self.current_task = current_task

    def __str__(self) -> str:
        return self.message


class ThrottlingError(Exception):
    """Raised when service capacity is exceeded (e.g., DynamoDB throttling)."""

    pass


class ResourceNotFoundError(Exception):
    """Raised when a required resource is not found (e.g., DynamoDB table missing)."""

    pass


class RepositoryError(Exception):
    """Raised when repository operations fail."""

    pass
