"""
API Gateway Test Helpers

Utility functions for creating API Gateway events for both unit and integration testing.
These helpers create realistic API Gateway events that can be used across all test types.
"""

import json
from typing import Any, Dict, Optional


def create_api_gateway_event(
    method: str = 'GET',
    path: str = '/tasks',
    body: Optional[Dict] = None,
    query_params: Optional[Dict] = None,
    path_params: Optional[Dict] = None,
    request_id: str = 'test-request-123',
) -> Dict[str, Any]:
    """
    Create a realistic API Gateway event for testing.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        path: Request path
        body: Request body as dictionary
        query_params: Query string parameters
        path_params: Path parameters
        request_id: Request ID for tracing (useful for test isolation)

    Returns:
        API Gateway event dictionary
    """
    return {
        'httpMethod': method,
        'path': path,
        'pathParameters': path_params or {},
        'queryStringParameters': query_params or {},
        'body': json.dumps(body) if body else None,
        'headers': {'Content-Type': 'application/json', 'Accept': 'application/json'},
        'requestContext': {
            'requestId': request_id,
            'stage': 'test',
            'accountId': '123456789012',
            'resourceId': 'test-resource',
            'httpMethod': method,
            'resourcePath': path,
            'protocol': 'HTTP/1.1',
            'requestTime': '09/Apr/2015:12:34:56 +0000',
            'requestTimeEpoch': 1428582896000,
            'identity': {'sourceIp': '127.0.0.1', 'userAgent': 'Custom User Agent String'},
        },
        'isBase64Encoded': False,
    }


def create_task_creation_event(
    title: str, priority: str = 'medium', description: Optional[str] = None, request_id: str = 'test-create-123'
) -> Dict[str, Any]:
    """Create API Gateway event for task creation."""
    body = {'title': title, 'priority': priority}
    if description:
        body['description'] = description

    return create_api_gateway_event(method='POST', path='/tasks', body=body, request_id=request_id)


def create_task_update_event(
    task_id: str, title: str, priority: str = 'medium', status: Optional[str] = None, version: int = 1, request_id: str = 'test-update-123'
) -> Dict[str, Any]:
    """Create API Gateway event for task update."""
    body = {'title': title, 'priority': priority, 'version': version}
    if status:
        body['status'] = status

    return create_api_gateway_event(method='PUT', path=f'/tasks/{task_id}', path_params={'task_id': task_id}, body=body, request_id=request_id)


def create_task_get_event(task_id: str, request_id: str = 'test-get-123') -> Dict[str, Any]:
    """Create API Gateway event for getting a task."""
    return create_api_gateway_event(method='GET', path=f'/tasks/{task_id}', path_params={'task_id': task_id}, request_id=request_id)


def create_task_delete_event(task_id: str, request_id: str = 'test-delete-123') -> Dict[str, Any]:
    """Create API Gateway event for task deletion."""
    return create_api_gateway_event(method='DELETE', path=f'/tasks/{task_id}', path_params={'task_id': task_id}, request_id=request_id)


def create_task_list_event(limit: Optional[int] = None, next_token: Optional[str] = None, request_id: str = 'test-list-123') -> Dict[str, Any]:
    """Create API Gateway event for listing tasks."""
    query_params = {}
    if limit:
        query_params['limit'] = str(limit)
    if next_token:
        query_params['next_token'] = next_token

    return create_api_gateway_event(method='GET', path='/tasks', query_params=query_params if query_params else None, request_id=request_id)


def create_invalid_method_event(request_id: str = 'test-invalid-123') -> Dict[str, Any]:
    """Create API Gateway event with unsupported HTTP method."""
    return create_api_gateway_event(method='PATCH', path='/tasks', request_id=request_id)


def create_invalid_json_event(request_id: str = 'test-invalid-json-123') -> Dict[str, Any]:
    """Create API Gateway event with invalid JSON body."""
    event = create_api_gateway_event(method='POST', path='/tasks', request_id=request_id)
    # Override body with invalid JSON
    event['body'] = 'invalid json content'
    return event


def create_missing_body_event(request_id: str = 'test-missing-body-123') -> Dict[str, Any]:
    """Create API Gateway event with missing body for POST request."""
    return create_api_gateway_event(method='POST', path='/tasks', body=None, request_id=request_id)
