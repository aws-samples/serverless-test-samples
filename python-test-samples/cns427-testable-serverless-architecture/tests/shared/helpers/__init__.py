"""Shared test helpers for dependency injection and test setup."""

from .api_gateway_helpers import (
    create_api_gateway_event,
    create_invalid_json_event,
    create_invalid_method_event,
    create_missing_body_event,
    create_task_creation_event,
    create_task_delete_event,
    create_task_get_event,
    create_task_list_event,
    create_task_update_event,
)
from .dependency_injection import domain_unit_dependencies, dynamodb_integration_dependencies, eventbridge_integration_dependencies
from .eventbridge_helpers import (
    check_test_infrastructure,
    cleanup_test_events,
    create_eventbridge_event,
    create_test_infrastructure_summary,
    extract_test_run_id_from_correlation_id,
    format_event_summary,
    generate_test_run_id,
    verify_event_structure,
    verify_task_event_data,
    wait_for_event_with_retries,
    wait_for_test_events,
)

__all__ = [
    # Dependency injection
    'dynamodb_integration_dependencies',
    'eventbridge_integration_dependencies',
    'domain_unit_dependencies',
    # API Gateway helpers
    'create_api_gateway_event',
    'create_task_creation_event',
    'create_task_update_event',
    'create_task_get_event',
    'create_task_delete_event',
    'create_task_list_event',
    'create_invalid_method_event',
    'create_invalid_json_event',
    'create_missing_body_event',
    # EventBridge helpers
    'generate_test_run_id',
    'wait_for_test_events',
    'cleanup_test_events',
    'verify_event_structure',
    'verify_task_event_data',
    'check_test_infrastructure',
    'create_test_infrastructure_summary',
    'wait_for_event_with_retries',
    'extract_test_run_id_from_correlation_id',
    'format_event_summary',
    'create_eventbridge_event',
]
