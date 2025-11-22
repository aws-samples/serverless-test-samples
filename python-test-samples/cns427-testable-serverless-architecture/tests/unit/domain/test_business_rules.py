"""Unit tests for business rules - pure logic, no mocks needed.

These tests verify the core business logic in isolation.
No external dependencies, no mocks, just pure functions and assertions.
"""

import pytest

from services.task_service.domain.business_rules import (
    can_transition_to,
    compare_version_tokens,
    has_circular_dependency,
    is_valid_version_token,
    validate_version_token_for_update,
)
from services.task_service.models.task import TaskStatus


class TestVersionTokenValidation:
    """Test version token validation rules."""

    def test_valid_version_token_positive_integer(self):
        """Valid version tokens are positive integer strings."""
        assert is_valid_version_token('1234567890') is True
        assert is_valid_version_token('1') is True
        assert is_valid_version_token('999999999999') is True

    def test_invalid_version_token_zero(self):
        """Zero is not a valid version token."""
        assert is_valid_version_token('0') is False

    def test_invalid_version_token_negative(self):
        """Negative numbers are not valid version tokens."""
        assert is_valid_version_token('-1') is False
        assert is_valid_version_token('-123') is False

    def test_invalid_version_token_empty(self):
        """Empty string is not a valid version token."""
        assert is_valid_version_token('') is False

    def test_invalid_version_token_non_numeric(self):
        """Non-numeric strings are not valid version tokens."""
        assert is_valid_version_token('abc') is False
        assert is_valid_version_token('12.34') is False
        assert is_valid_version_token('12a34') is False

    def test_invalid_version_token_none(self):
        """None is not a valid version token."""
        assert is_valid_version_token(None) is False

    def test_compare_version_tokens_older(self):
        """Older token should return -1."""
        assert compare_version_tokens('100', '200') == -1
        assert compare_version_tokens('1', '999') == -1

    def test_compare_version_tokens_newer(self):
        """Newer token should return 1."""
        assert compare_version_tokens('200', '100') == 1
        assert compare_version_tokens('999', '1') == 1

    def test_compare_version_tokens_equal(self):
        """Equal tokens should return 0."""
        assert compare_version_tokens('123', '123') == 0
        assert compare_version_tokens('1', '1') == 0

    def test_compare_version_tokens_invalid_raises_error(self):
        """Comparing invalid tokens should raise ValueError."""
        with pytest.raises(ValueError, match='Invalid version token'):
            compare_version_tokens('invalid', '123')

        with pytest.raises(ValueError, match='Invalid version token'):
            compare_version_tokens('123', 'invalid')

    def test_validate_version_token_for_update_valid(self):
        """Valid version token should not raise error."""
        validate_version_token_for_update('123456')  # Should not raise

    def test_validate_version_token_for_update_empty_raises_error(self):
        """Empty version token should raise ValueError."""
        with pytest.raises(ValueError, match='required for update'):
            validate_version_token_for_update('')

    def test_validate_version_token_for_update_invalid_format_raises_error(self):
        """Invalid format should raise ValueError."""
        with pytest.raises(ValueError, match='Invalid version_token format'):
            validate_version_token_for_update('invalid')

        with pytest.raises(ValueError, match='Invalid version_token format'):
            validate_version_token_for_update('0')


class TestStatusTransitions:
    """Test task status transition rules."""

    def test_pending_to_in_progress_allowed(self):
        """PENDING -> IN_PROGRESS is allowed."""
        assert can_transition_to(TaskStatus.PENDING, TaskStatus.IN_PROGRESS) is True

    def test_pending_to_completed_allowed(self):
        """PENDING -> COMPLETED is allowed (skip in_progress)."""
        assert can_transition_to(TaskStatus.PENDING, TaskStatus.COMPLETED) is True

    def test_pending_to_pending_not_allowed(self):
        """PENDING -> PENDING is not allowed (no-op)."""
        assert can_transition_to(TaskStatus.PENDING, TaskStatus.PENDING) is False

    def test_in_progress_to_completed_allowed(self):
        """IN_PROGRESS -> COMPLETED is allowed."""
        assert can_transition_to(TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED) is True

    def test_in_progress_to_pending_not_allowed(self):
        """IN_PROGRESS -> PENDING is not allowed (can't go backwards)."""
        assert can_transition_to(TaskStatus.IN_PROGRESS, TaskStatus.PENDING) is False

    def test_in_progress_to_in_progress_not_allowed(self):
        """IN_PROGRESS -> IN_PROGRESS is not allowed (no-op)."""
        assert can_transition_to(TaskStatus.IN_PROGRESS, TaskStatus.IN_PROGRESS) is False

    def test_completed_to_pending_allowed(self):
        """COMPLETED -> PENDING is allowed (reopen task)."""
        assert can_transition_to(TaskStatus.COMPLETED, TaskStatus.PENDING) is True

    def test_completed_to_in_progress_not_allowed(self):
        """COMPLETED -> IN_PROGRESS is not allowed."""
        assert can_transition_to(TaskStatus.COMPLETED, TaskStatus.IN_PROGRESS) is False

    def test_completed_to_completed_not_allowed(self):
        """COMPLETED -> COMPLETED is not allowed (no-op)."""
        assert can_transition_to(TaskStatus.COMPLETED, TaskStatus.COMPLETED) is False


class TestCircularDependencies:
    """Test circular dependency detection rules."""

    def test_self_dependency_is_circular(self):
        """Task depending on itself is circular."""
        assert has_circular_dependency('task-1', 'task-1', {}) is True

    def test_no_dependencies_not_circular(self):
        """Task with no dependencies is not circular."""
        assert has_circular_dependency('task-1', 'task-2', {}) is False

    def test_simple_circular_dependency(self):
        """Simple cycle: A -> B -> A."""
        dependencies = {'task-B': ['task-A']}
        assert has_circular_dependency('task-A', 'task-B', dependencies) is True

    def test_three_way_circular_dependency(self):
        """Three-way cycle: A -> B -> C -> A."""
        dependencies = {'task-B': ['task-C'], 'task-C': ['task-A']}
        assert has_circular_dependency('task-A', 'task-B', dependencies) is True

    def test_complex_circular_dependency(self):
        """Complex cycle: A -> B -> C -> D -> B."""
        dependencies = {'task-B': ['task-C'], 'task-C': ['task-D'], 'task-D': ['task-B']}
        assert has_circular_dependency('task-A', 'task-B', dependencies) is True

    def test_linear_dependency_not_circular(self):
        """Linear chain: A -> B -> C -> D (no cycle)."""
        dependencies = {'task-B': ['task-C'], 'task-C': ['task-D'], 'task-D': []}
        assert has_circular_dependency('task-A', 'task-B', dependencies) is False

    def test_diamond_dependency_not_circular(self):
        """Diamond pattern: A -> B,C -> D (no cycle)."""
        dependencies = {'task-B': ['task-D'], 'task-C': ['task-D'], 'task-D': []}
        assert has_circular_dependency('task-A', 'task-B', dependencies) is False
        assert has_circular_dependency('task-A', 'task-C', dependencies) is False

    def test_multiple_paths_one_circular(self):
        """Multiple paths where one creates a cycle."""
        dependencies = {
            'task-B': ['task-C', 'task-D'],
            'task-C': ['task-E'],
            'task-D': ['task-A'],  # This creates the cycle
            'task-E': [],
        }
        assert has_circular_dependency('task-A', 'task-B', dependencies) is True

    def test_deep_dependency_chain_not_circular(self):
        """Deep chain without cycle."""
        dependencies = {'task-B': ['task-C'], 'task-C': ['task-D'], 'task-D': ['task-E'], 'task-E': ['task-F'], 'task-F': []}
        assert has_circular_dependency('task-A', 'task-B', dependencies) is False

    def test_dependency_on_unrelated_task(self):
        """Dependency on task not in the chain is not circular."""
        dependencies = {'task-B': ['task-X'], 'task-X': ['task-Y'], 'task-Y': []}
        assert has_circular_dependency('task-A', 'task-B', dependencies) is False
