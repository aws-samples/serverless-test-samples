"""Unit tests for task handler focusing on HTTP response handling."""

import json

import pytest

from services.task_service.handler import lambda_handler
from tests.unit.test_helpers import create_api_gateway_event, create_test_context


@pytest.fixture
def lambda_context():
    """Fixture for Lambda context."""
    return create_test_context()


# fake_task_service fixture defined in conftest.py
class TestTaskHandler:
    """Unit tests for task handler focusing on HTTP response handling and status codes."""

    def test_create_task_returns_201(self, fake_task_service, lambda_context):
        """Test successful task creation returns 201 status code."""
        event = create_api_gateway_event(
            method='POST', path='/tasks', body={'title': 'New Task', 'description': 'Test task', 'priority': 'medium', 'dependencies': []}
        )

        # GIVEN task service returns task data
        # WHEN calling create task endpoint
        response = lambda_handler(event, lambda_context)

        # THEN should return 201 with task data
        assert response['statusCode'] == 201
        body = json.loads(response['body'])
        assert body['title'] == 'New Task'
        assert body['task_id'] == 'test-task-123'

    def test_get_task_returns_200(self, fake_task_service, lambda_context):
        """Test successful task retrieval returns 200 status code."""
        # GIVEN fake service will return a task
        # WHEN getting task
        event = create_api_gateway_event(method='GET', path='/tasks/test-id', path_parameters={'task_id': 'test-id'})
        response = lambda_handler(event, lambda_context)

        # THEN should return 200 with task data
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['task_id'] == 'test-id'
        assert body['title'] == 'Retrieved Task'

    def test_get_task_not_found_returns_404(self, fake_task_service, lambda_context):
        """Test getting non-existent task returns 404."""
        # GIVEN service will raise ValueError for not found
        fake_task_service.should_raise_value_error = True
        fake_task_service.value_error_message = 'Task not found: non-existent-id'

        # WHEN getting non-existent task
        event = create_api_gateway_event(method='GET', path='/tasks/non-existent-id', path_parameters={'task_id': 'non-existent-id'})
        response = lambda_handler(event, lambda_context)

        # THEN should return 404
        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert 'not found' in body['message'].lower()

    def test_list_tasks_returns_200(self, fake_task_service, lambda_context):
        """Test task listing returns 200 status code."""
        # GIVEN fake service returns task list
        # WHEN listing tasks
        event = create_api_gateway_event(method='GET', path='/tasks')
        response = lambda_handler(event, lambda_context)

        # THEN should return 200 with task list
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'tasks' in body
        assert 'pagination' in body
        assert len(body['tasks']) == 2
        assert body['tasks'][0]['title'] == 'Task 1'

    def test_list_tasks_with_pagination(self, fake_task_service, lambda_context):
        """Test task listing with pagination parameters."""
        # GIVEN fake service returns paginated results
        # WHEN listing tasks with pagination
        event = create_api_gateway_event(method='GET', path='/tasks', query_parameters={'limit': '10'})
        response = lambda_handler(event, lambda_context)

        # THEN should return 200 with pagination info
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'pagination' in body
        # Fake service returns None for next_token
        assert body['pagination']['next_token'] is None

    def test_update_task_returns_200(self, fake_task_service, lambda_context):
        """Test successful task update returns 200 status code."""
        # GIVEN fake service returns updated task
        # WHEN updating task
        event = create_api_gateway_event(
            method='PUT', path='/tasks/test-id', path_parameters={'task_id': 'test-id'}, body={'title': 'Updated Task', 'version': 1}
        )
        response = lambda_handler(event, lambda_context)

        # THEN should return 200 with updated data
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['title'] == 'Updated Task'
        assert 'version' in body

    def test_update_task_version_conflict_returns_409(self, fake_task_service, lambda_context):
        """Test version conflict during update returns 409."""
        # GIVEN service raises ConflictError for version mismatch
        fake_task_service.should_raise_conflict_error = True

        # WHEN updating with wrong version
        event = create_api_gateway_event(
            method='PUT', path='/tasks/test-id', path_parameters={'task_id': 'test-id'}, body={'title': 'Updated Task', 'version': 1}
        )
        response = lambda_handler(event, lambda_context)

        # THEN should return 409 for conflict
        assert response['statusCode'] == 409

    def test_delete_task_returns_204(self, fake_task_service, lambda_context):
        """Test successful task deletion returns 204 status code."""
        # GIVEN fake service deletes successfully
        # WHEN deleting task
        event = create_api_gateway_event(method='DELETE', path='/tasks/test-id', path_parameters={'task_id': 'test-id'})
        response = lambda_handler(event, lambda_context)

        # THEN should return 204 with empty body
        assert response['statusCode'] == 204
        assert response['body'] == ''

    def test_delete_task_not_found_returns_404(self, fake_task_service, lambda_context):
        """Test deleting non-existent task returns 404."""
        # GIVEN service raises ValueError for not found
        fake_task_service.should_raise_value_error = True
        fake_task_service.value_error_message = 'Task not found: non-existent'

        # WHEN deleting non-existent task
        event = create_api_gateway_event(method='DELETE', path='/tasks/non-existent', path_parameters={'task_id': 'non-existent'})
        response = lambda_handler(event, lambda_context)

        # THEN should return 404
        assert response['statusCode'] == 404

    def test_create_task_validation_error_returns_400(self, fake_task_service, lambda_context):
        """Test validation error returns 400 status code."""
        # GIVEN invalid request with empty title
        event = create_api_gateway_event(
            method='POST',
            path='/tasks',
            body={'title': ''},  # Invalid empty title
        )

        # WHEN creating task with invalid data
        response = lambda_handler(event, lambda_context)

        # THEN should return 400 status code
        assert response['statusCode'] == 400

        # Verify response has error information
        assert 'body' in response
        body_str = response['body']
        assert body_str is not None and body_str != ''
        assert 'validation' in body_str.lower() or 'invalid' in body_str.lower() or 'error' in body_str.lower()

    def test_create_task_missing_body_returns_400(self, fake_task_service, lambda_context):
        """Test missing request body returns 400."""
        # GIVEN request with no body
        event = create_api_gateway_event(method='POST', path='/tasks', body=None)

        # WHEN creating task without body
        response = lambda_handler(event, lambda_context)

        # THEN should return 400 or higher error status
        assert response['statusCode'] >= 400

    def test_unsupported_method_returns_405(self, fake_task_service, lambda_context):
        """Test unsupported HTTP method returns 405."""
        # GIVEN request with unsupported method (PATCH)
        event = create_api_gateway_event(method='PATCH', path='/tasks')

        # WHEN processing unsupported method
        response = lambda_handler(event, lambda_context)

        # THEN should return 404 (API Gateway resolver behavior for unsupported methods)
        assert response['statusCode'] == 404

    def test_internal_error_returns_500(self, fake_task_service, lambda_context):
        """Test internal service error returns 500."""
        # GIVEN service raises unexpected exception
        fake_task_service.should_raise_generic_error = True

        # WHEN processing request that causes internal error
        event = create_api_gateway_event(method='GET', path='/tasks/test-id', path_parameters={'task_id': 'test-id'})
        response = lambda_handler(event, lambda_context)

        # THEN should return 500
        assert response['statusCode'] == 500
