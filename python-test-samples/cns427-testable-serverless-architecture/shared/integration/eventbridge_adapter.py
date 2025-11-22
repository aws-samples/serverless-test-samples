"""EventBridge adapter for publishing task events."""

import json
import os
import time

import boto3
from aws_lambda_powertools import Logger
from botocore.exceptions import ClientError

from services.task_service.domain.exceptions import RepositoryError
from services.task_service.models.task import TaskEvent
from shared.integration.interfaces import EventPublisher

logger = Logger()

# Initialize AWS clients at module level
AWS_REGION = os.environ.get('AWS_REGION', 'us-west-2')
events_client = boto3.client('events', region_name=AWS_REGION)


def _handle_eventbridge_error(e: ClientError, operation: str) -> None:
    """Convert EventBridge ClientError to domain exceptions."""
    error_code = e.response['Error']['Code']

    # All EventBridge errors are internal system issues, not client-facing capacity issues
    # So we use RepositoryError (500) instead of ThrottlingError (503)
    if error_code == 'ThrottlingException':
        raise RepositoryError(f'EventBridge capacity exceeded during {operation}: {error_code}') from e
    elif error_code in ['AccessDeniedException', 'UnauthorizedException']:
        raise RepositoryError(f'Permission error accessing EventBridge during {operation}: {error_code}') from e
    elif error_code in ['InternalException', 'ServiceUnavailableException']:
        raise RepositoryError(f'EventBridge service error during {operation}: {error_code}') from e
    else:
        raise RepositoryError(f'EventBridge error during {operation}: {error_code}') from e


class EventBridgePublisher(EventPublisher):
    """EventBridge implementation of EventPublisher."""

    def __init__(self, event_bus_name: str = 'default'):
        """Initialize EventBridge publisher."""
        self.event_bus_name = event_bus_name
        self.events_client = events_client
        self.max_retries = 3
        self.base_delay = 0.1

    def publish_event(self, event: TaskEvent) -> None:
        """Publish a task event to EventBridge with retry logic."""
        for attempt in range(self.max_retries):
            try:
                # Use the event's to_eventbridge_entry method
                entry = event.to_eventbridge_entry(event_bus_name=self.event_bus_name)
                logger.debug(f'Publishing event: {json.dumps(entry)}')

                response = self.events_client.put_events(Entries=[entry])

                # Check for failed entries
                if response.get('FailedEntryCount', 0) > 0:
                    failed_entries = response.get('Entries', [])
                    error_msg = f'Failed to publish event: {failed_entries}'
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)

                logger.info(f'Published event: {event.event_type}')
                return

            except ClientError as e:
                error_code = e.response['Error']['Code']

                # Don't retry on certain errors
                if error_code in ['ValidationException', 'InvalidParameterException']:
                    logger.error(f'Non-retryable error publishing event: {e}')
                    _handle_eventbridge_error(e, 'publish_event')

                # Retry on throttling and service errors
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2**attempt)  # Exponential backoff
                    logger.warning(f'Retrying event publish in {delay}s (attempt {attempt + 1})')
                    time.sleep(delay)
                else:
                    logger.error(f'Failed to publish event after {self.max_retries} attempts: {e}')
                    _handle_eventbridge_error(e, 'publish_event')

            except Exception as e:
                logger.error(f'Unexpected error publishing event: {e}')
                raise
