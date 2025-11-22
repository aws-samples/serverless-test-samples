"""
EventBridge Test Helpers

Utility functions for EventBridge testing including event verification,
cleanup, and infrastructure management. These helpers can be used across
both unit and integration tests.
"""

import json
import time
import uuid
from typing import Any, Dict, List, Optional

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError


def generate_test_run_id() -> str:
    """Generate a unique test run ID for event isolation."""
    return f'test-{uuid.uuid4()}'


def wait_for_test_events(test_run_id: str, expected_count: int, timeout: int = 30, table_name: str = 'cns427-task-api-test-results') -> List[Dict]:
    """
    Poll test results table for expected events with timeout.

    Args:
        test_run_id: Unique test run identifier
        expected_count: Number of events to wait for
        timeout: Maximum time to wait in seconds
        table_name: DynamoDB table name for test results

    Returns:
        List of captured events sorted by timestamp

    Raises:
        TimeoutError: If expected events not received within timeout
    """
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(table_name)

    start_time = time.time()
    events = []

    while time.time() - start_time < timeout:
        try:
            response = table.query(
                KeyConditionExpression=Key('test_run_id').eq(test_run_id),
                ScanIndexForward=False,  # Latest events first
            )

            events = response.get('Items', [])
            if len(events) >= expected_count:
                return sorted(events, key=lambda x: x['event_timestamp'])

        except ClientError as e:
            # Table might not exist yet or other transient errors
            print(f'Warning: Error querying test results table: {e}')
        except Exception as e:
            print(f'Unexpected error querying test results: {e}')

        time.sleep(1)

    raise TimeoutError(f"Expected {expected_count} events for test_run_id '{test_run_id}', got {len(events)} after {timeout}s")


def cleanup_test_events(test_run_id: str, table_name: str = 'cns427-task-api-test-results') -> int:
    """
    Clean up test events from results table.

    Args:
        test_run_id: Unique test run identifier
        table_name: DynamoDB table name for test results

    Returns:
        Number of events cleaned up
    """
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table(table_name)

        # Query all events for this test run
        response = table.query(KeyConditionExpression=Key('test_run_id').eq(test_run_id))

        events = response.get('Items', [])

        # Delete each event
        deleted_count = 0
        for item in events:
            try:
                table.delete_item(Key={'test_run_id': item['test_run_id'], 'event_timestamp': item['event_timestamp']})
                deleted_count += 1
            except Exception as e:
                print(f'Warning: Failed to delete event {item["event_timestamp"]}: {e}')

        return deleted_count

    except Exception as e:
        print(f'Warning: Failed to cleanup test events for {test_run_id}: {e}')
        return 0


def verify_event_structure(event_data: Dict, expected_event_type: str) -> bool:
    """
    Verify that captured event has expected structure and content.

    Args:
        event_data: Parsed event data from test results
        expected_event_type: Expected event type (e.g., 'TaskCreated')

    Returns:
        True if event structure is valid
    """
    required_fields = ['event_type', 'task_id', 'correlation_id']

    # Check required fields
    for field in required_fields:
        if field not in event_data:
            print(f'Missing required field: {field}')
            return False

    # Check event type
    if event_data['event_type'] != expected_event_type:
        print(f"Expected event_type '{expected_event_type}', got '{event_data['event_type']}'")
        return False

    # Check correlation_id format (should start with TEST-)
    correlation_id = event_data.get('correlation_id', '')
    if not correlation_id.startswith('TEST-'):
        print(f'Invalid correlation_id format: {correlation_id}')
        return False

    return True


def verify_task_event_data(event_data: Dict, expected_task_data: Dict) -> bool:
    """
    Verify that task event contains expected task data.

    Args:
        event_data: Parsed event data from test results
        expected_task_data: Expected task data fields

    Returns:
        True if task data matches expectations
    """
    task_data = event_data.get('task_data', {})

    for key, expected_value in expected_task_data.items():
        if key not in task_data:
            print(f'Missing task data field: {key}')
            return False

        if task_data[key] != expected_value:
            print(f"Task data mismatch for {key}: expected '{expected_value}', got '{task_data[key]}'")
            return False

    return True


def check_test_infrastructure() -> Dict[str, bool]:
    """
    Check if test infrastructure is properly deployed.

    Returns:
        Dictionary with infrastructure component status
    """
    status = {'test_results_table': False, 'eventbridge_rule': False, 'test_subscriber_lambda': False}

    try:
        # Check DynamoDB table
        dynamodb = boto3.client('dynamodb', region_name='us-east-1')
        try:
            dynamodb.describe_table(TableName='cns427-task-api-test-results')
            status['test_results_table'] = True
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceNotFoundException':
                print(f'Error checking test results table: {e}')

        # Check EventBridge rule
        events = boto3.client('events', region_name='us-east-1')
        try:
            response = events.list_rules(NamePrefix='cns427-task-api-test')
            if response.get('Rules'):
                status['eventbridge_rule'] = True
        except Exception as e:
            print(f'Error checking EventBridge rule: {e}')

        # Check Lambda function
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        try:
            lambda_client.get_function(FunctionName='cns427-task-api-test-subscriber')
            status['test_subscriber_lambda'] = True
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceNotFoundException':
                print(f'Error checking test subscriber Lambda: {e}')

    except Exception as e:
        print(f'Error checking test infrastructure: {e}')

    return status


def create_test_infrastructure_summary() -> str:
    """
    Create a summary of test infrastructure status for debugging.

    Returns:
        Formatted string with infrastructure status
    """
    status = check_test_infrastructure()

    summary = 'EventBridge Test Infrastructure Status:\n'
    summary += f'  ✓ Test Results Table: {"✓" if status["test_results_table"] else "✗"}\n'
    summary += f'  ✓ EventBridge Rule: {"✓" if status["eventbridge_rule"] else "✗"}\n'
    summary += f'  ✓ Test Subscriber Lambda: {"✓" if status["test_subscriber_lambda"] else "✗"}\n'

    if not all(status.values()):
        summary += '\nTo deploy test infrastructure:\n'
        summary += '  poetry run cdk deploy --context environment=test\n'

    return summary


def wait_for_event_with_retries(test_run_id: str, expected_count: int, max_retries: int = 3, base_timeout: int = 30) -> List[Dict]:
    """
    Wait for events with exponential backoff retries.

    Args:
        test_run_id: Unique test run identifier
        expected_count: Number of events to wait for
        max_retries: Maximum number of retry attempts
        base_timeout: Base timeout for each attempt

    Returns:
        List of captured events

    Raises:
        TimeoutError: If events not received after all retries
    """
    for attempt in range(max_retries):
        timeout = base_timeout * (2**attempt)  # Exponential backoff

        try:
            return wait_for_test_events(test_run_id, expected_count, timeout)
        except TimeoutError as e:
            if attempt == max_retries - 1:
                # Last attempt, re-raise the error
                raise e

            print(f'Attempt {attempt + 1} failed, retrying with longer timeout...')
            time.sleep(2)  # Brief pause between retries

    # This should never be reached due to the re-raise above
    raise TimeoutError(f'Failed to receive events after {max_retries} attempts')


def extract_test_run_id_from_correlation_id(correlation_id: str) -> Optional[str]:
    """
    Extract test run ID from correlation ID.

    Args:
        correlation_id: Correlation ID in format TEST-{test_run_id}-{original_id}

    Returns:
        Test run ID or None if format is invalid
    """
    if not correlation_id.startswith('TEST-'):
        return None

    parts = correlation_id.split('-', 2)
    if len(parts) < 2:
        return None

    return parts[1]


def format_event_summary(events: List[Dict]) -> str:
    """
    Format a summary of captured events for debugging.

    Args:
        events: List of captured events

    Returns:
        Formatted string with event summary
    """
    if not events:
        return 'No events captured'

    summary = f'Captured {len(events)} events:\n'

    for i, event in enumerate(events, 1):
        event_data = json.loads(event['event_data'])
        summary += f'  {i}. {event_data["event_type"]} - Task: {event_data["task_id"]}\n'
        summary += f'     Timestamp: {event["event_timestamp"]}\n'

        if 'task_data' in event_data:
            task_data = event_data['task_data']
            summary += f'     Title: {task_data.get("title", "N/A")}\n'
            summary += f'     Priority: {task_data.get("priority", "N/A")}\n'

    return summary


def create_eventbridge_event(
    source: str = 'task-api', detail_type: str = 'Task Event', detail: Dict = None, event_bus_name: str = 'default'
) -> Dict[str, Any]:
    """
    Create an EventBridge event for testing.

    Args:
        source: Event source
        detail_type: Event detail type
        detail: Event detail payload
        event_bus_name: EventBridge bus name

    Returns:
        EventBridge event dictionary
    """
    return {'Source': source, 'DetailType': detail_type, 'Detail': json.dumps(detail or {}), 'EventBusName': event_bus_name, 'Time': time.time()}
