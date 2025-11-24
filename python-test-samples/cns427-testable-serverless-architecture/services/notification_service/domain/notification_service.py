"""Domain logic for notification processing."""

from typing import Any, Dict

from aws_lambda_powertools import Logger

logger = Logger()


class NotificationService:
    """Pure business logic for notification processing."""

    def process_task_event(self, event_type: str, task_data: Dict[str, Any]) -> None:
        """Process a task event and generate appropriate notification."""
        logger.info(f'Processing task event: {event_type}')
        logger.debug(f'Event data: {task_data}')

        if event_type == 'TaskCreated':
            self._handle_task_created(task_data)
        elif event_type == 'TaskUpdated':
            self._handle_task_updated(task_data)
        elif event_type == 'TaskDeleted':
            self._handle_task_deleted(task_data)
        else:
            logger.warning(f'Unknown event type: {event_type}')

    def _handle_task_created(self, task_data: Dict[str, Any]) -> None:
        """Handle task created notification."""
        task_id = task_data.get('task_id')
        title = task_data.get('title')
        priority = task_data.get('priority')

        logger.debug(f'Handling TaskCreated: task_id={task_id}, priority={priority}')
        logger.info(
            f'Task created notification: {title}',
            extra={'task_id': task_id, 'event_type': 'TaskCreated'},
        )

    def _handle_task_updated(self, task_data: Dict[str, Any]) -> None:
        """Handle task updated notification."""
        task_id = task_data.get('task_id')
        title = task_data.get('title')
        status = task_data.get('status')
        version = task_data.get('version')

        logger.debug(f'Handling TaskUpdated: task_id={task_id}, status={status}, version={version}')
        logger.info(
            f'Task updated notification: {title} (status: {status})',
            extra={
                'task_id': task_id,
                'event_type': 'TaskUpdated',
                'new_status': status,
            },
        )

    def _handle_task_deleted(self, task_data: Dict[str, Any]) -> None:
        """Handle task deleted notification."""
        task_id = task_data.get('task_id')

        logger.debug(f'Handling TaskDeleted: task_id={task_id}')
        logger.info(
            f'Task deleted notification: {task_id}',
            extra={'task_id': task_id, 'event_type': 'TaskDeleted'},
        )
