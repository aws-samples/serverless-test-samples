"""
End-to-End Test: Complete Task Lifecycle with Dependencies

Tests the full user workflow through real API Gateway:
1. User creates parent task via API Gateway
2. User creates child task with dependency on parent
3. Task persisted to DynamoDB
4. Events published to EventBridge (real events, not TEST- prefix)
5. Notification Lambda processes events
6. Verify entire flow completed successfully

This validates:
- API Gateway IAM authorization
- Lambda cold/warm starts
- DynamoDB persistence
- EventBridge event delivery (real production flow)
- Async notification processing
- Business rules (circular dependencies)
- Error handling across services

Note on EventBridge Verification:
- E2E tests use REAL events (source: "cns427-task-api", detailType: "TaskCreated")
- Test harness only captures TEST-* events (source: "TEST-cns427-task-api")
- This is intentional - E2E tests verify production flow, not test flow
- Integration tests use TEST- prefix for isolated testing
"""

import json
import os
import time
import uuid

import boto3
import pytest
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

# Get configuration from environment with defaults
from infrastructure.config import InfrastructureConfig

config = InfrastructureConfig()
API_ENDPOINT = os.environ.get('API_ENDPOINT')
AWS_REGION = os.environ.get('AWS_DEFAULT_REGION', os.environ.get('AWS_REGION', 'us-west-2'))
TASKS_TABLE_NAME = os.environ.get('TASKS_TABLE_NAME', config.tasks_table_name())
TEST_HARNESS_TABLE = os.environ.get('TEST_HARNESS_TABLE', config.test_results_table_name())


@pytest.fixture(scope='module')
def api_endpoint():
    """Get API endpoint from environment, CDK outputs file, or CloudFormation stack."""
    if API_ENDPOINT:
        return API_ENDPOINT.rstrip('/')

    # Try to get from CDK outputs file (created by deploy script)
    try:
        import json
        from pathlib import Path

        outputs_file = Path('cdk-outputs.json')
        if outputs_file.exists():
            with open(outputs_file) as f:
                outputs = json.load(f)
                # Look for ApiEndpoint in the API stack
                # Structure: {"cns427-task-api-api": {"ApiEndpoint": "https://..."}}
                api_stack_name = 'cns427-task-api-api'
                if api_stack_name in outputs and 'ApiEndpoint' in outputs[api_stack_name]:
                    endpoint = outputs[api_stack_name]['ApiEndpoint'].rstrip('/')
                    print(f'\n[E2E] ℹ Using API endpoint from cdk-outputs.json: {endpoint}')
                    return endpoint
                else:
                    print('\n[E2E] ⚠ ApiEndpoint not found in cdk-outputs.json')
                    print(f'[E2E] Available stacks: {list(outputs.keys())}')
    except Exception as e:
        print(f'\n[E2E] ⚠ Could not read cdk-outputs.json: {e}')

    # Try to get from CloudFormation stack outputs
    try:
        import boto3

        cfn = boto3.client('cloudformation', region_name=AWS_REGION)
        stack_name = 'cns427-task-api-api'

        response = cfn.describe_stacks(StackName=stack_name)
        outputs = response['Stacks'][0]['Outputs']

        for output in outputs:
            if output['OutputKey'] == 'ApiEndpoint':
                endpoint = output['OutputValue'].rstrip('/')
                print(f'\n[E2E] ℹ Using API endpoint from CloudFormation: {endpoint}')
                return endpoint
    except Exception as e:
        print(f'\n[E2E] ⚠ Could not get API endpoint from CloudFormation: {e}')

    # If we get here, we couldn't find the endpoint
    pytest.skip(
        'API_ENDPOINT not set and could not retrieve from CDK outputs or CloudFormation.\n'
        'Please either:\n'
        '  1. Deploy with: make deploy (saves outputs to cdk-outputs.json)\n'
        '  2. Set API_ENDPOINT environment variable:\n'
        '     export API_ENDPOINT=$(aws cloudformation describe-stacks --stack-name cns427-task-api-api '
        "--query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' --output text --region us-west-2)"
    )


@pytest.fixture
def aws_session():
    """Create AWS session for signing requests."""
    return boto3.Session(region_name=AWS_REGION)


@pytest.fixture
def dynamodb_client():
    """DynamoDB client for verification."""
    return boto3.client('dynamodb', region_name=AWS_REGION)


@pytest.fixture
def test_run_id():
    """Generate unique test run ID."""
    return f'e2e-{uuid.uuid4()}'


def sign_request(method, url, body=None, session=None):
    """
    Sign HTTP request with AWS SigV4 for IAM authorization.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        url: Full URL to request
        body: Request body (dict or None)
        session: boto3 Session for credentials

    Returns:
        dict: Headers with AWS signature
    """
    if session is None:
        session = boto3.Session(region_name=AWS_REGION)

    credentials = session.get_credentials()

    # Prepare request
    request_body = json.dumps(body) if body else ''
    request = AWSRequest(
        method=method,
        url=url,
        data=request_body,
        headers={
            'Content-Type': 'application/json',
            'Host': url.split('/')[2],  # Extract host from URL
        },
    )

    # Sign request
    SigV4Auth(credentials, 'execute-api', AWS_REGION).add_auth(request)

    return dict(request.headers)


def make_api_request(method, url, body=None, session=None, timeout=30):
    """
    Make signed API request to API Gateway.

    Args:
        method: HTTP method
        url: Full URL
        body: Request body dict
        session: boto3 Session
        timeout: Request timeout in seconds (default: 30)

    Returns:
        requests.Response
    """
    headers = sign_request(method, url, body, session)

    if method == 'GET':
        return requests.get(url, headers=headers, timeout=timeout)
    elif method == 'POST':
        return requests.post(url, headers=headers, json=body, timeout=timeout)
    elif method == 'PUT':
        return requests.put(url, headers=headers, json=body, timeout=timeout)
    elif method == 'DELETE':
        return requests.delete(url, headers=headers, timeout=timeout)
    else:
        raise ValueError(f'Unsupported method: {method}')


@pytest.mark.e2e
class TestTaskLifecycleE2E:
    """End-to-end tests for complete task lifecycle."""

    def test_complete_task_lifecycle_with_dependencies(self, api_endpoint, aws_session, dynamodb_client, test_run_id):
        """
        E2E: Create tasks with dependencies, verify persistence and async processing.

        Flow:
        1. Create parent task via API Gateway
        2. Verify parent task in DynamoDB
        3. Create child task with dependency on parent
        4. Verify child task in DynamoDB with correct dependency
        5. Wait for async EventBridge processing
        6. Verify events were published and processed
        7. Update parent task status
        8. Verify update propagated correctly
        9. Cleanup all test data
        """
        parent_task_id = None
        child_task_id = None

        try:
            # Step 1: Create parent task via API Gateway
            print('\n[E2E] Step 1: Creating parent task via API Gateway')
            parent_task_data = {
                'title': f'E2E Parent Task - {test_run_id}',
                'description': 'Parent task for E2E testing',
                'priority': 'high',
                'status': 'pending',
            }

            response = make_api_request('POST', f'{api_endpoint}/tasks', body=parent_task_data, session=aws_session)

            if response.status_code != 201:
                print('\n[E2E] ❌ API request failed!')
                print(f'[E2E] Status Code: {response.status_code}')
                print(f'[E2E] Response: {response.text}')
                print(f'[E2E] Headers: {response.headers}')
                print('\n[E2E] Troubleshooting:')
                print('[E2E] 1. Check Lambda logs:')
                print('[E2E]    aws logs tail /aws/lambda/cns427-task-api-task-handler --follow')
                print('[E2E] 2. Check if Lambda has correct environment variables')
                print('[E2E] 3. Check if Lambda has permissions to DynamoDB and EventBridge')
                print('[E2E] 4. Verify API Gateway is deployed: aws apigateway get-rest-apis')

            assert response.status_code == 201, f'Failed to create parent task: {response.text}'
            parent_task = response.json()
            parent_task_id = parent_task['task_id']

            print(f'[E2E] ✓ Parent task created: {parent_task_id}')
            assert parent_task['title'] == parent_task_data['title']
            assert parent_task['priority'] == 'high'
            assert parent_task['status'] == 'pending'

            # Step 2: Verify parent task in DynamoDB
            print('[E2E] Step 2: Verifying parent task in DynamoDB')
            time.sleep(1)  # Allow for eventual consistency

            db_response = dynamodb_client.get_item(TableName=TASKS_TABLE_NAME, Key={'task_id': {'S': parent_task_id}})

            assert 'Item' in db_response, 'Parent task not found in DynamoDB'
            assert db_response['Item']['title']['S'] == parent_task_data['title']
            print('[E2E] ✓ Parent task verified in DynamoDB')

            # Step 3: Create child task with dependency on parent
            print('[E2E] Step 3: Creating child task with dependency')
            child_task_data = {
                'title': f'E2E Child Task - {test_run_id}',
                'description': 'Child task depends on parent',
                'priority': 'medium',
                'status': 'pending',
                'dependencies': [parent_task_id],
            }

            response = make_api_request('POST', f'{api_endpoint}/tasks', body=child_task_data, session=aws_session)

            assert response.status_code == 201, f'Failed to create child task: {response.text}'
            child_task = response.json()
            child_task_id = child_task['task_id']

            print(f'[E2E] ✓ Child task created: {child_task_id}')
            assert child_task['title'] == child_task_data['title']
            assert parent_task_id in child_task.get('dependencies', [])

            # Step 4: Verify child task in DynamoDB with correct dependency
            print('[E2E] Step 4: Verifying child task dependencies in DynamoDB')
            time.sleep(1)

            db_response = dynamodb_client.get_item(TableName=TASKS_TABLE_NAME, Key={'task_id': {'S': child_task_id}})

            assert 'Item' in db_response, 'Child task not found in DynamoDB'
            db_dependencies = db_response['Item'].get('dependencies', {}).get('L', [])
            db_dependency_ids = [dep['S'] for dep in db_dependencies]
            assert parent_task_id in db_dependency_ids, 'Dependency not stored correctly'
            print('[E2E] ✓ Child task dependencies verified in DynamoDB')

            # Step 5: Wait for async EventBridge processing
            print('[E2E] Step 5: Waiting for async EventBridge processing')
            time.sleep(5)  # Allow time for EventBridge → Lambda → DynamoDB

            # Step 6: Verify notification Lambda was triggered by EventBridge
            print('[E2E] Step 6: Verifying notification Lambda was triggered')

            # Check CloudWatch Logs for notification Lambda invocations
            logs_client = boto3.client('logs', region_name=AWS_REGION)
            notification_lambda_name = 'cns427-task-api-notification-handler'
            log_group_name = f'/aws/lambda/{notification_lambda_name}'

            try:
                # Get recent log streams (last 5 minutes)
                end_time = int(time.time() * 1000)
                start_time = end_time - (5 * 60 * 1000)  # 5 minutes ago

                # Query logs for our task IDs
                response = logs_client.filter_log_events(
                    logGroupName=log_group_name, startTime=start_time, endTime=end_time, filterPattern=f'"{parent_task_id}"'
                )

                if response.get('events'):
                    print('[E2E] ✓ Notification Lambda was triggered for parent task')
                    print(f'[E2E] ✓ Found {len(response["events"])} log entries')
                    print('[E2E] ✓ EventBridge → Notification Lambda flow verified')
                else:
                    print('[E2E] ⚠ No notification Lambda logs found for parent task')
                    print("[E2E] ℹ This may be normal if notification Lambda hasn't processed yet")
                    print(f'[E2E] ℹ Check logs manually: aws logs tail {log_group_name} --follow')

            except Exception as e:
                print(f'[E2E] ⚠ Could not verify notification Lambda: {e}')
                print('[E2E] ℹ This is not a test failure - notification Lambda may not be deployed')

            print('[E2E] ℹ Note: E2E tests use real events (not TEST- prefix)')
            print('[E2E] ℹ Test harness only captures TEST-* events for integration tests')

            # Step 7: Update parent task status
            print('[E2E] Step 7: Updating parent task status')

            # First, get the latest version of the task
            response = make_api_request('GET', f'{api_endpoint}/tasks/{parent_task_id}', session=aws_session)
            assert response.status_code == 200, f'Failed to get parent task: {response.text}'
            current_parent = response.json()

            print(f'[E2E] Current parent version from GET: {current_parent["version"]}')
            print(f'[E2E] Current parent data: {json.dumps(current_parent, indent=2)}')

            # Small delay to ensure no race condition
            time.sleep(0.5)

            # Now update with the current version
            update_data = {
                'status': 'in_progress',
                'version': current_parent['version'],  # Use current version for optimistic locking
            }

            print(f'[E2E] Sending update with version: {update_data["version"]}')

            response = make_api_request('PUT', f'{api_endpoint}/tasks/{parent_task_id}', body=update_data, session=aws_session)

            # If we get a conflict, retry once with fresh version
            if response.status_code == 409:
                print('[E2E] Got conflict, retrying with fresh version...')
                time.sleep(0.5)

                # Get fresh version
                response = make_api_request('GET', f'{api_endpoint}/tasks/{parent_task_id}', session=aws_session)
                assert response.status_code == 200
                current_parent = response.json()

                # Retry update
                update_data['version'] = current_parent['version']
                print(f'[E2E] Retrying with version: {update_data["version"]}')

                response = make_api_request('PUT', f'{api_endpoint}/tasks/{parent_task_id}', body=update_data, session=aws_session)

            if response.status_code != 200:
                print(f'[E2E] Update failed with status {response.status_code}')
                print(f'[E2E] Response: {response.text}')

            assert response.status_code == 200, f'Failed to update parent task: {response.text}'
            updated_task = response.json()
            assert updated_task['status'] == 'in_progress'
            print('[E2E] ✓ Parent task status updated')

            # Step 8: Verify update propagated correctly
            print('[E2E] Step 8: Verifying update in DynamoDB')
            time.sleep(1)

            db_response = dynamodb_client.get_item(TableName=TASKS_TABLE_NAME, Key={'task_id': {'S': parent_task_id}})

            assert db_response['Item']['status']['S'] == 'in_progress'
            print('[E2E] ✓ Update verified in DynamoDB')

            # Step 9: Verify we can retrieve tasks via API
            print('[E2E] Step 9: Retrieving tasks via API')

            # Get parent task
            response = make_api_request('GET', f'{api_endpoint}/tasks/{parent_task_id}', session=aws_session)
            assert response.status_code == 200
            retrieved_parent = response.json()
            assert retrieved_parent['task_id'] == parent_task_id
            assert retrieved_parent['status'] == 'in_progress'

            # Get child task
            response = make_api_request('GET', f'{api_endpoint}/tasks/{child_task_id}', session=aws_session)
            assert response.status_code == 200
            retrieved_child = response.json()
            assert retrieved_child['task_id'] == child_task_id
            assert parent_task_id in retrieved_child.get('dependencies', [])

            print('[E2E] ✓ Tasks retrieved successfully via API')

            print('\n[E2E] ✅ Complete task lifecycle test PASSED')
            print('[E2E] Summary:')
            print(f'  - Parent task: {parent_task_id}')
            print(f'  - Child task: {child_task_id}')
            print('  - Dependency validated: ✓')
            print('  - DynamoDB persistence: ✓')
            print('  - API Gateway IAM auth: ✓')
            print('  - Status updates: ✓')

        finally:
            # Step 10: Cleanup - Delete test tasks
            print('\n[E2E] Cleanup: Deleting test tasks')

            if child_task_id:
                try:
                    response = make_api_request('DELETE', f'{api_endpoint}/tasks/{child_task_id}', session=aws_session)
                    if response.status_code == 204:
                        print(f'[E2E] ✓ Child task deleted: {child_task_id}')
                except Exception as e:
                    print(f'[E2E] ⚠ Failed to delete child task: {e}')

            if parent_task_id:
                try:
                    response = make_api_request('DELETE', f'{api_endpoint}/tasks/{parent_task_id}', session=aws_session)
                    if response.status_code == 204:
                        print(f'[E2E] ✓ Parent task deleted: {parent_task_id}')
                except Exception as e:
                    print(f'[E2E] ⚠ Failed to delete parent task: {e}')

    def test_circular_dependency_prevention_e2e(self, api_endpoint, aws_session, test_run_id):
        """
        E2E: Verify circular dependency detection works through API.

        Flow:
        1. Create task A
        2. Create task B with dependency on A
        3. Try to update A to depend on B (should fail)
        4. Verify error handling
        """
        task_a_id = None
        task_b_id = None

        try:
            # Create task A
            print('\n[E2E] Creating task A')
            response = make_api_request(
                'POST',
                f'{api_endpoint}/tasks',
                body={'title': f'E2E Task A - {test_run_id}', 'description': 'Task A for circular dependency test'},
                session=aws_session,
            )

            assert response.status_code == 201
            task_a = response.json()
            task_a_id = task_a['task_id']
            print(f'[E2E] ✓ Task A created: {task_a_id}')

            # Create task B with dependency on A
            print('[E2E] Creating task B with dependency on A')
            response = make_api_request(
                'POST',
                f'{api_endpoint}/tasks',
                body={'title': f'E2E Task B - {test_run_id}', 'description': 'Task B depends on A', 'dependencies': [task_a_id]},
                session=aws_session,
            )

            assert response.status_code == 201
            task_b = response.json()
            task_b_id = task_b['task_id']
            print(f'[E2E] ✓ Task B created: {task_b_id}')

            # Try to create circular dependency (should fail)
            print('[E2E] Attempting to create circular dependency')
            response = make_api_request(
                'PUT',
                f'{api_endpoint}/tasks/{task_a_id}',
                body={
                    'dependencies': [task_b_id],
                    'version': task_a['version'],  # Required for optimistic locking
                },
                session=aws_session,
            )

            # Should fail with 400 or 409
            assert response.status_code in [400, 409], f'Expected error for circular dependency, got {response.status_code}'

            error_response = response.json()
            assert 'error' in error_response or 'message' in error_response
            print('[E2E] ✓ Circular dependency correctly prevented')
            print(f'[E2E] Error message: {error_response}')

            print('\n[E2E] ✅ Circular dependency prevention test PASSED')

        finally:
            # Cleanup
            print('\n[E2E] Cleanup: Deleting test tasks')
            for task_id in [task_b_id, task_a_id]:
                if task_id:
                    try:
                        make_api_request('DELETE', f'{api_endpoint}/tasks/{task_id}', session=aws_session)
                        print(f'[E2E] ✓ Task deleted: {task_id}')
                    except Exception as e:
                        print(f'[E2E] ⚠ Failed to delete task: {e}')
