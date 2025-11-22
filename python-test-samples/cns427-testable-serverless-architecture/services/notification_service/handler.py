"""Lambda handler for processing task events from EventBridge."""

import json
from typing import Any, Dict, Optional

from aws_lambda_powertools import Logger
from aws_lambda_powertools.logging import correlation_paths

from services.notification_service.domain.notification_service import NotificationService
from services.task_service.models.task import TaskEvent

logger = Logger()

# Dependencies - injected at runtime
notification_service: Optional[NotificationService] = None


def _initialize_dependencies():
    """Initialize dependencies with dependency injection."""
    global notification_service

    if notification_service is None:
        notification_service = NotificationService()


@logger.inject_lambda_context(correlation_id_path=correlation_paths.EVENT_BRIDGE)
def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Lambda handler entry point for EventBridge events.

    EventBridge Event Structure:
    {
        "version": "0",
        "id": "event-id",
        "detail-type": "TaskCreated",
        "source": "cns427-task-api",
        "account": "123456789012",
        "time": "2025-11-15T02:15:28Z",
        "region": "us-west-2",
        "resources": [],
        "detail": {
            "task_id": "abc-123",
            "title": "My Task",
            ...
        }
    }
    """
    _initialize_dependencies()

    logger.info('Notification handler invoked')
    logger.debug(f'Event: {json.dumps(event)}')

    try:
        # Extract EventBridge event fields
        detail = event.get('detail', {})
        detail_type = event.get('detail-type', '')
        source = event.get('source', '')

        if not detail:
            logger.warning('No event detail found to process')
            return {'statusCode': 200, 'processedEvents': 0}

        if not detail_type:
            logger.warning('No detail-type found in event')
            return {'statusCode': 200, 'processedEvents': 0}

        logger.debug(f'Processing EventBridge event: source={source}, detail_type={detail_type}')

        # Parse EventBridge event into TaskEvent model
        task_event = TaskEvent.from_eventbridge_event(event)

        logger.debug(f'Event type: {task_event.event_type} (original: {detail_type})')

        # Extract task_id for logging
        task_id = task_event.task_data.get('task_id', 'unknown')

        logger.info(f'Processing {task_event.event_type} event for task: {task_id}')

        # Delegate to domain service
        if notification_service is None:
            raise RuntimeError('Notification service not initialized')
        notification_service.process_task_event(task_event.event_type, task_event.task_data)

        logger.info(f'Successfully processed {task_event.event_type} event for task: {task_id}')
        return {'statusCode': 200, 'processedEvents': 1}

    except Exception as e:
        # Log as warning since we're re-raising for Lambda to handle
        # Lambda runtime will log the error and trigger retry mechanism
        logger.warning(f'Handler encountered error, re-raising for Lambda retry: {e}', exc_info=True)
        # Re-raise to trigger Lambda retry mechanism
        raise
