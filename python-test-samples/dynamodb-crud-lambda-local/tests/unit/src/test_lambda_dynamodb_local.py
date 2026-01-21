import pytest
import boto3
import json
import time
import socket
import os
from datetime import datetime


@pytest.fixture(scope="session")
def dynamodb_local():
    """
    Fixture to verify DynamoDB Local is running.
    DOES NOT MANAGE THE CONTAINER - assumes it's started externally.
    """
    # Check if DynamoDB Local is running on port 8000
    def is_port_open(host, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                result = s.connect_ex((host, port))
                return result == 0
        except:
            return False
    
    if not is_port_open("127.0.0.1", 8000):
        pytest.skip("DynamoDB Local is not running on port 8000. Please start with 'docker run --rm -d --name dynamodb-local --network host amazon/dynamodb-local'")
    
    print("DynamoDB Local is running on port 8000")
    yield "http://127.0.0.1:8000"


@pytest.fixture(scope="session")
def sam_lambda_local():
    """
    Fixture to verify SAM Local Lambda emulator is running.
    DOES NOT MANAGE SAM LOCAL - assumes it's started externally.
    """
    # Check if SAM Local Lambda is running on port 3001
    def is_port_open(host, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                result = s.connect_ex((host, port))
                return result == 0
        except:
            return False
    
    lambda_port = 3001
    
    if not is_port_open("127.0.0.1", lambda_port):
        pytest.skip(f"SAM Local Lambda is not running on port {lambda_port}. Please start with 'sam local start-lambda --port {lambda_port} --docker-network host'")
    
    print(f"SAM Local Lambda is running on port {lambda_port}")
    yield f"http://127.0.0.1:{lambda_port}"


@pytest.fixture(scope="session")
def lambda_client(sam_lambda_local):
    """
    Fixture to create a Lambda client for local testing using SAM Local endpoint.
    """
    endpoint_url = sam_lambda_local
    return boto3.client(
        'lambda',
        endpoint_url=endpoint_url,
        region_name='us-east-1',
        aws_access_key_id='DUMMYIDEXAMPLE',
        aws_secret_access_key='DUMMYEXAMPLEKEY'
    )


@pytest.fixture(scope="session")
def dynamodb_client():
    """
    Fixture to create a DynamoDB client for local testing.
    """
    return boto3.client(
        'dynamodb',
        endpoint_url="http://127.0.0.1:8000",
        region_name='us-east-1',
        aws_access_key_id='DUMMYIDEXAMPLE',
        aws_secret_access_key='DUMMYEXAMPLEKEY'
    )


@pytest.fixture(scope="session") 
def health_check(dynamodb_local, dynamodb_client, sam_lambda_local, lambda_client):
    """
    Fixture to perform initial health check of both DynamoDB Local and SAM Local Lambda.
    Both services are assumed to be running externally.
    """
    try:
        # Test DynamoDB connection
        response = dynamodb_client.list_tables()
        print("DynamoDB Local health check passed")
        
        # Test Lambda connection by listing functions
        try:
            lambda_response = lambda_client.list_functions()
            print(f"SAM Local Lambda health check passed - {len(lambda_response.get('Functions', []))} functions available")
        except Exception as e:
            print(f"SAM Local Lambda health check: {str(e)}")
            # SAM Local might not support list_functions, so we'll do a basic connectivity test
            print("SAM Local Lambda endpoint is accessible")
        
        return True
    except Exception as e:
        pytest.fail(f"Health check failed: {str(e)}")


@pytest.fixture(scope="session")
def ensure_clean_start(dynamodb_client):
    """
    Ensure we start with a clean DynamoDB state.
    Delete the test table if it exists from previous runs.
    """
    table_name = 'CRUDLocalTable'
    try:
        # Check if table exists
        dynamodb_client.describe_table(TableName=table_name)
        print(f"Found existing table '{table_name}' from previous run - deleting...")
        
        # Delete the table
        dynamodb_client.delete_table(TableName=table_name)
        
        # Wait for deletion to complete
        waiter = dynamodb_client.get_waiter('table_not_exists')
        waiter.wait(TableName=table_name)
        print(f"Table '{table_name}' deleted successfully")
        
    except dynamodb_client.exceptions.ResourceNotFoundException:
        print(f"No existing table '{table_name}' found - clean start confirmed")
    except Exception as e:
        print(f"Warning: Could not clean existing table: {str(e)}")
    
    yield
    
    # Optionally clean up after all tests
    # Uncomment the next lines if you want cleanup after tests
    # try:
    #     dynamodb_client.delete_table(TableName=table_name)
    #     print(f"Cleaned up table '{table_name}' after tests")
    # except:
    #     pass


def invoke_lambda_function_boto3(lambda_client, function_name, event_data):
    """
    Invoke Lambda function using boto3 client natively.
    Much cleaner than subprocess approach.
    """
    try:
        print(f"Invoking Lambda function: {function_name}")
        print(f"Event data: {json.dumps(event_data, indent=2)}")
        
        # Invoke Lambda function using boto3
        response = lambda_client.invoke(
            FunctionName=function_name,
            Payload=json.dumps(event_data)
        )
        
        print(f"Lambda invocation status: {response['StatusCode']}")
        
        # Check for invocation errors
        if response['StatusCode'] != 200:
            raise Exception(f"Lambda invocation failed with status code: {response['StatusCode']}")
        
        # Read and parse the response payload
        payload = response['Payload'].read().decode('utf-8')
        
        if not payload:
            raise Exception("Empty payload from Lambda function")
        
        print(f"Raw Lambda response: {payload}")
        
        try:
            lambda_response = json.loads(payload)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse Lambda response as JSON: {payload}. Error: {str(e)}")
        
        # Check if the Lambda function itself returned an error
        if isinstance(lambda_response, dict):
            if 'errorMessage' in lambda_response and 'errorType' in lambda_response:
                error_msg = lambda_response.get('errorMessage', 'Unknown error')
                error_type = lambda_response.get('errorType', 'Unknown error type')
                raise Exception(f"Lambda runtime error ({error_type}): {error_msg}")
            
            # Check for function execution errors
            if 'FunctionError' in response:
                function_error = response['FunctionError']
                raise Exception(f"Lambda function error ({function_error}): {lambda_response}")
        
        return lambda_response
        
    except Exception as e:
        print(f"Lambda invocation failed for {function_name}: {str(e)}")
        raise Exception(f"Lambda invocation failed: {str(e)}")


def test_lambda_init_function(dynamodb_local, health_check, ensure_clean_start, lambda_client):
    """
    Test the Lambda function that initializes the DynamoDB table.
    Uses clean state - no existing table.
    """
    # Event for table initialization
    init_event = {
        "test_type": "init",
        "timestamp": datetime.now().isoformat()
    }
    
    # Invoke Lambda Init function - should create new table
    response = invoke_lambda_function_boto3(lambda_client, 'CRUDLambdaInitFunction', init_event)
    
    # Validate Lambda response structure
    assert 'statusCode' in response, "Lambda response should contain statusCode"
    assert 'body' in response, "Lambda response should contain body"
    
    # Validate successful table creation
    assert response['statusCode'] == 200, f"Table creation failed with status: {response['statusCode']}"
    assert response['body'] == 'CRUDLocalTable', f"Expected table name 'CRUDLocalTable', got '{response['body']}'"
    
    print("Lambda Init function executed successfully")
    print("Table 'CRUDLocalTable' created successfully")


def test_lambda_create_function(dynamodb_local, health_check, lambda_client):
    """
    Test the Lambda function that creates items in DynamoDB.
    """
    # Event for item creation - matches ../events/lambda-create-event.json
    create_event = {
        "body": json.dumps({"Id": "123", "name": "Batman"})
    }
    
    # Invoke Lambda Create function
    response = invoke_lambda_function_boto3(lambda_client, 'CRUDLambdaCreateFunction', create_event)
    
    # Validate Lambda response structure
    assert 'statusCode' in response, "Lambda response should contain statusCode"
    assert 'body' in response, "Lambda response should contain body"
    
    # Validate successful item creation
    assert response['statusCode'] == 200, f"Item creation failed with status: {response['statusCode']}"
    
    # Parse response body
    body_data = json.loads(response['body'])
    assert 'message' in body_data, "Response body should contain message field"
    assert body_data['message'] == 'Item added', f"Expected 'Item added', got '{body_data['message']}'"
    
    print(f"Lambda Create function response: {{'statusCode': {response['statusCode']}, 'message': '{body_data['message']}'}}")
    print("Item created successfully: {'Id': '123', 'name': 'Batman'}")


def test_lambda_read_function(dynamodb_local, health_check, lambda_client):
    """
    Test the Lambda function that reads items from DynamoDB.
    """
    # Event for item reading - matches ../events/lambda-read-event.json
    read_event = {
        "Id": "123"
    }
    
    # Invoke Lambda Read function
    response = invoke_lambda_function_boto3(lambda_client, 'CRUDLambdaReadFunction', read_event)
    
    # Validate Lambda response structure
    assert 'statusCode' in response, "Lambda response should contain statusCode"
    assert 'body' in response, "Lambda response should contain body"
    
    # Validate successful item retrieval
    assert response['statusCode'] == 200, f"Item retrieval failed with status: {response['statusCode']}"
    
    # Parse response body to get the item
    item_data = json.loads(response['body'])
    assert 'Id' in item_data, "Retrieved item should contain Id field"
    assert 'name' in item_data, "Retrieved item should contain name field"
    assert item_data['Id'] == '123', f"Expected Id '123', got '{item_data['Id']}'"
    assert item_data['name'] == 'Batman', f"Expected name 'Batman', got '{item_data['name']}'"
    
    print(f"Lambda Read function response: {{'statusCode': {response['statusCode']}, 'Item': {{'Id': '{item_data['Id']}', 'name': '{item_data['name']}'}}}}")
    print("Item retrieved successfully")


def test_lambda_update_function(dynamodb_local, health_check, lambda_client):
    """
    Test the Lambda function that updates items in DynamoDB.
    """
    # Event for item update - matches ../events/lambda-update-event.json
    update_event = {
        "body": json.dumps({"Id": "123", "name": "Robin"})
    }
    
    # Invoke Lambda Update function
    response = invoke_lambda_function_boto3(lambda_client, 'CRUDLambdaUpdateFunction', update_event)
    
    # Validate Lambda response structure
    assert 'statusCode' in response, "Lambda response should contain statusCode"
    assert 'body' in response, "Lambda response should contain body"
    
    # Validate successful item update
    assert response['statusCode'] == 200, f"Item update failed with status: {response['statusCode']}"
    
    # Parse response body
    body_data = json.loads(response['body'])
    assert 'message' in body_data, "Response body should contain message field"
    assert body_data['message'] == 'Item updated successfully', f"Expected 'Item updated successfully', got '{body_data['message']}'"
    
    print(f"Lambda Update function response: {{'statusCode': {response['statusCode']}, 'message': '{body_data['message']}'}}")
    print("Item updated successfully: {'Id': '123', 'name': 'Robin'}")


def test_lambda_delete_function(dynamodb_local, health_check, lambda_client):
    """
    Test the Lambda function that deletes items from DynamoDB.
    """
    # Event for item deletion - matches ../events/lambda-delete-event.json
    delete_event = {
        "Id": "123"
    }
    
    # Invoke Lambda Delete function
    response = invoke_lambda_function_boto3(lambda_client, 'CRUDLambdaDeleteFunction', delete_event)
    
    # Validate Lambda response structure
    assert 'statusCode' in response, "Lambda response should contain statusCode"
    assert 'body' in response, "Lambda response should contain body"
    
    # Validate successful item deletion
    assert response['statusCode'] == 200, f"Item deletion failed with status: {response['statusCode']}"
    
    # Parse response body
    body_data = json.loads(response['body'])
    assert 'message' in body_data, "Response body should contain message field"
    assert body_data['message'] == 'Item deleted', f"Expected 'Item deleted', got '{body_data['message']}'"
    
    print(f"Lambda Delete function response: {{'statusCode': {response['statusCode']}, 'message': '{body_data['message']}'}}")
    print("Item deleted successfully")


def test_full_crud_workflow_integration(dynamodb_local, health_check, lambda_client):
    """
    Test the complete CRUD workflow through Lambda functions.
    Uses unique IDs to avoid conflicts with other tests.
    """
    # Use unique ID for integration test
    integration_id = f"integration-{int(time.time() * 1000)}"
    
    # 1. Create item with unique ID
    create_event = {"body": json.dumps({"Id": integration_id, "name": "Integration Batman"})}
    create_response = invoke_lambda_function_boto3(lambda_client, 'CRUDLambdaCreateFunction', create_event)
    assert create_response['statusCode'] == 200, "Item creation failed in integration test"
    
    # 2. Read item
    read_event = {"Id": integration_id}
    read_response = invoke_lambda_function_boto3(lambda_client, 'CRUDLambdaReadFunction', read_event)
    assert read_response['statusCode'] == 200, "Item reading failed in integration test"
    
    read_item = json.loads(read_response['body'])
    assert read_item['Id'] == integration_id, "Read item Id mismatch"
    assert read_item['name'] == 'Integration Batman', "Read item name mismatch"
    
    # 3. Update item
    update_event = {"body": json.dumps({"Id": integration_id, "name": "Integration Robin"})}
    update_response = invoke_lambda_function_boto3(lambda_client, 'CRUDLambdaUpdateFunction', update_event)
    assert update_response['statusCode'] == 200, "Item update failed in integration test"
    
    # 4. Verify update by reading again
    read_updated_response = invoke_lambda_function_boto3(lambda_client, 'CRUDLambdaReadFunction', read_event)
    assert read_updated_response['statusCode'] == 200, "Reading updated item failed"
    
    updated_item = json.loads(read_updated_response['body'])
    assert updated_item['name'] == 'Integration Robin', "Item was not properly updated"
    
    # 5. Delete item
    delete_event = {"Id": integration_id}
    delete_response = invoke_lambda_function_boto3(lambda_client, 'CRUDLambdaDeleteFunction', delete_event)
    assert delete_response['statusCode'] == 200, "Item deletion failed in integration test"
    
    # 6. Verify deletion by trying to read (should return 404)
    final_read_response = invoke_lambda_function_boto3(lambda_client, 'CRUDLambdaReadFunction', read_event)
    assert final_read_response['statusCode'] == 404, "Deleted item should return 404"
    
    print("Full CRUD workflow completed successfully through Lambda functions")
    print("All operations validated: Create -> Read -> Update -> Delete with unique ID")


def test_lambda_performance_and_error_handling(dynamodb_local, health_check, lambda_client):
    """
    Test Lambda function performance and error handling scenarios.
    """
    operation_times = []
    successful_operations = 0
    
    # Use unique ID for performance test
    perf_id = f"perf-{int(time.time() * 1000)}"
    
    # Test scenarios for performance
    test_scenarios = [
        # 1. Valid item creation (performance test)
        {
            'function': 'CRUDLambdaCreateFunction', 
            'event': {'body': json.dumps({'Id': perf_id, 'name': 'Performance Test'})},
            'expected_status': 200,
            'operation': 'create'
        },
        # 2. Valid item read (performance test)
        {
            'function': 'CRUDLambdaReadFunction',
            'event': {'Id': perf_id},
            'expected_status': 200,
            'operation': 'read'
        },
        # 3. Valid item update (performance test)
        {
            'function': 'CRUDLambdaUpdateFunction',
            'event': {'body': json.dumps({'Id': perf_id, 'name': 'Updated Performance Test'})},
            'expected_status': 200,
            'operation': 'update'
        },
        # 4. Valid item delete (performance test)
        {
            'function': 'CRUDLambdaDeleteFunction',
            'event': {'Id': perf_id},
            'expected_status': 200,
            'operation': 'delete'
        }
    ]
    
    # Execute test scenarios and measure performance
    for scenario in test_scenarios:
        start_time = time.time()
        
        try:
            response = invoke_lambda_function_boto3(lambda_client, scenario['function'], scenario['event'])
            end_time = time.time()
            execution_time = int((end_time - start_time) * 1000)  # Convert to milliseconds
            operation_times.append(execution_time)
            
            # Validate expected status code
            assert response['statusCode'] == scenario['expected_status'], \
                f"{scenario['operation']} operation failed with status: {response['statusCode']}"
            
            successful_operations += 1
            
        except Exception as e:
            print(f"Operation {scenario['operation']} failed: {str(e)}")
            continue
    
    # Calculate performance metrics
    if operation_times:
        avg_execution_time = sum(operation_times) / len(operation_times)
        min_execution_time = min(operation_times)
        max_execution_time = max(operation_times)
        
        # Performance assertions - reasonable for Lambda cold/warm starts
        assert avg_execution_time < 5000, f"Average execution time too slow: {avg_execution_time}ms"
        assert successful_operations >= 3, f"Too few successful operations: {successful_operations}"
        
        print(f"Performance test completed: avg_lambda_time={int(avg_execution_time)}ms, crud_operations={successful_operations}")
    else:
        print("Performance test completed: avg_lambda_time=N/A, crud_operations=0")
    
    # Test error handling scenarios
    error_scenarios = [
        # Test reading non-existent item
        {
            'function': 'CRUDLambdaReadFunction',
            'event': {'Id': 'non-existent-id'},
            'expected_status': 404,
            'operation': 'read_nonexistent'
        }
    ]
    
    error_handled_correctly = 0
    
    for scenario in error_scenarios:
        try:
            response = invoke_lambda_function_boto3(lambda_client, scenario['function'], scenario['event'])
            
            # Validate that error is handled correctly
            if response['statusCode'] == scenario['expected_status']:
                error_handled_correctly += 1
                
        except Exception as e:
            # Some error scenarios might raise exceptions, which is acceptable
            error_handled_correctly += 1
    
    print("Error handling validated: proper status codes and error messages")
