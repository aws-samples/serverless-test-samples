"""Lambda handler for task CRUD operations."""

from typing import Any, Dict, Optional

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.event_handler.exceptions import BadRequestError, InternalServerError, NotFoundError, ServiceError
from aws_lambda_powertools.logging import correlation_paths
from botocore.exceptions import ClientError
from pydantic import ValidationError

from services.task_service.domain.exceptions import CircularDependencyError, ConflictError, RepositoryError, ResourceNotFoundError, ThrottlingError
from services.task_service.domain.task_service import TaskService
from services.task_service.models.api import CreateTaskRequest, ErrorResponse, PaginationInfo, TaskResponse, UpdateTaskRequest

logger = Logger()
app = APIGatewayRestResolver()

# Domain service - injected at runtime
task_service: Optional[TaskService] = None


def _initialize_dependencies():
    """Initialize dependencies with dependency injection."""
    global task_service

    if task_service is None:
        task_service = TaskService()


def _handle_common_exceptions(e: Exception, operation: str = 'operation', task_id: Optional[str] = None):
    """
    Handle common exceptions across all endpoints.

    Args:
        e: The exception to handle
        operation: Description of the operation (e.g., "creating task", "updating task")
        task_id: Optional task ID for logging context

    Raises:
        Appropriate Powertools exception or returns error response tuple
    """
    extra_context = {'task_id': task_id} if task_id else {}

    # Domain exceptions
    if isinstance(e, ThrottlingError):
        logger.warning(f'Throttling error during {operation}: {str(e)}', extra={'retry_recommended': True, **extra_context})
        raise ServiceError(503, 'Service temporarily unavailable due to high load. Please retry after a few seconds.')

    if isinstance(e, ResourceNotFoundError):
        logger.error(f'Resource not found during {operation}: {str(e)}', extra={'error_type': 'configuration', **extra_context})
        raise InternalServerError('Service configuration error. Please contact support.')

    if isinstance(e, RepositoryError):
        logger.error(f'Repository error during {operation}: {str(e)}', extra=extra_context)
        raise InternalServerError('Database error occurred. Please try again later.')

    if isinstance(e, ConflictError):
        logger.warning(f'Conflict during {operation}: {str(e)}', extra={'conflict_reason': 'version_mismatch', **extra_context})
        # Serialize current_task to JSON-compatible format
        current_task_serialized = None
        if e.current_task:
            import json
            from datetime import datetime

            # Convert datetime objects to ISO format strings
            current_task_serialized = json.loads(json.dumps(e.current_task, default=lambda o: o.isoformat() if isinstance(o, datetime) else str(o)))
        return {'error': 'Conflict', 'message': str(e), 'current_task': current_task_serialized}, 409

    if isinstance(e, CircularDependencyError):
        logger.warning(f'Circular dependency error during {operation}: {str(e)}', extra=extra_context)
        error = ErrorResponse(error='BusinessError', message=str(e), details=None)
        raise BadRequestError(error.model_dump_json())

    # AWS SDK exceptions
    if isinstance(e, ClientError):
        logger.error(f'AWS service error during {operation}: {e}', extra=extra_context)
        error = ErrorResponse(error='InternalError', message=f'Failed {operation}', details=None)
        return error.model_dump(), 500

    # Validation exceptions
    if isinstance(e, ValidationError):
        logger.warning(f'Validation error during {operation}: {e}', extra=extra_context)
        error = ErrorResponse(error='ValidationError', message='Invalid request data', details={'errors': e.errors()})
        raise BadRequestError(error.model_dump_json())

    # Business logic exceptions
    if isinstance(e, ValueError):
        logger.warning(f'Business logic error during {operation}: {e}', extra=extra_context)
        error_msg = str(e).lower()

        if 'not found' in error_msg:
            error = ErrorResponse(error='NotFound', message=str(e), details=None)
            raise NotFoundError(error.model_dump_json())
        elif 'version' in error_msg:
            error = ErrorResponse(error='ConflictError', message=str(e), details=None)
            return error.model_dump(), 409
        else:
            error = ErrorResponse(error='BusinessError', message=str(e), details=None)
            raise BadRequestError(error.model_dump_json())

    # Catch-all for unexpected exceptions
    logger.error(f'Unexpected error during {operation}: {str(e)}', extra=extra_context)
    raise InternalServerError('Internal server error')


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """Lambda handler entry point."""
    _initialize_dependencies()
    return app.resolve(event, context)


@app.post('/tasks')
def create_task():
    """Create a new task."""
    try:
        # Parse and validate request
        request_data = app.current_event.json_body
        create_request = CreateTaskRequest.model_validate(request_data)

        # Delegate to domain service
        created_task = task_service.create_task(create_request)

        # Return response
        logger.info(f'Created task: {created_task.task_id}')
        return TaskResponse.from_task(created_task).model_dump(), 201

    except Exception as e:
        result = _handle_common_exceptions(e, 'creating task')
        if result:
            return result
        raise


@app.get('/tasks/<task_id>')
def get_task(task_id: str):
    """Retrieve a task by ID."""
    try:
        if task_service is None:
            raise RuntimeError('Task service not initialized')
        task = task_service.get_task(task_id)

        logger.info(f'Retrieved task: {task_id}')
        return TaskResponse.from_task(task).model_dump()

    except Exception as e:
        result = _handle_common_exceptions(e, 'retrieving task', task_id)
        if result:
            return result
        raise


@app.get('/tasks')
def list_tasks():
    """List tasks with pagination."""
    try:
        # Parse query parameters
        limit = app.current_event.query_string_parameters.get('limit')
        next_token = app.current_event.query_string_parameters.get('next_token')

        # Delegate to domain service
        tasks, next_page_token = task_service.list_tasks(int(limit) if limit else None, next_token)

        # Build response
        task_responses = [TaskResponse.from_task(task).model_dump() for task in tasks]
        pagination = PaginationInfo(limit=len(tasks), next_token=next_page_token)

        logger.info(f'Listed {len(tasks)} tasks')
        return {'tasks': task_responses, 'pagination': pagination.model_dump()}

    except Exception as e:
        result = _handle_common_exceptions(e, 'listing tasks')
        if result:
            return result
        raise


@app.put('/tasks/<task_id>')
def update_task(task_id: str):
    """Update an existing task."""
    try:
        # Parse and validate request
        request_data = app.current_event.json_body
        update_request = UpdateTaskRequest.model_validate(request_data)

        logger.debug(f'Update request for task {task_id}: {update_request.model_dump()}')

        # Delegate to domain service
        if task_service is None:
            raise RuntimeError('Task service not initialized')
        updated_task = task_service.update_task(task_id, update_request)

        logger.debug(f'Update successful for task {task_id}, new version: {updated_task.version}')

        # Return response
        logger.info(f'Updated task: {task_id}')
        return TaskResponse.from_task(updated_task).model_dump()

    except Exception as e:
        logger.debug(f'Update failed for task {task_id}: {type(e).__name__}: {str(e)}')
        result = _handle_common_exceptions(e, 'updating task', task_id)
        if result:
            return result
        raise


@app.delete('/tasks/<task_id>')
def delete_task(task_id: str):
    """Delete a task."""
    try:
        # Delegate to domain service
        if task_service is None:
            raise RuntimeError('Task service not initialized')
        task_service.delete_task(task_id)

        logger.info(f'Deleted task: {task_id}')
        return '', 204

    except Exception as e:
        result = _handle_common_exceptions(e, 'deleting task', task_id)
        if result:
            return result
        raise
