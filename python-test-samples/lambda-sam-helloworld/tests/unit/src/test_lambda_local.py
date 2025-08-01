import pytest
import boto3
import json
import time
import socket
from datetime import datetime
import concurrent.futures

@pytest.fixture(scope="session")
def lambda_container():
    """
    Fixture to verify SAM Local Lambda emulator is running.
    This fixture assumes the emulator is already started externally.
    """
    # Check if Lambda emulator is running on port 3001
    def is_port_open(host, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                result = s.connect_ex((host, port))
                return result == 0
        except:
            return False
    
    if not is_port_open("127.0.0.1", 3001):
        pytest.skip("SAM Local Lambda emulator is not running on port 3001. Please start with 'sam local start-lambda -p 3001'")
    
    print("SAM Local Lambda emulator is running on port 3001")
    yield "http://127.0.0.1:3001"


@pytest.fixture(scope="session")
def lambda_client():
    """
    Fixture to create a Lambda client for local testing.
    """
    return boto3.client(
        'lambda',
        endpoint_url="http://127.0.0.1:3001",
        region_name='us-east-1',
        aws_access_key_id='DUMMYIDEXAMPLE',
        aws_secret_access_key='DUMMYEXAMPLEKEY'
    )


@pytest.fixture(scope="session")
def health_check(lambda_container, lambda_client):
    """
    Fixture to perform initial health check of the Lambda function.
    """
    # Simple test event
    test_event = {
        "test": "health_check",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName='LambdaHelloWorld',
            Payload=json.dumps(test_event)
        )
        
        if response['StatusCode'] == 200:
            print("Lambda function is responding correctly")
            return True
        else:
            pytest.fail(f"Lambda health check failed with status: {response['StatusCode']}")
            
    except Exception as e:
        pytest.fail(f"Lambda health check failed: {str(e)}")


def test_lambda_basic_hello_world(lambda_client, health_check):
    """
    Test the basic Lambda function invocation.
    Validates the default "Hello World!" message response.
    """
    # Basic test event
    test_event = {
        "test_type": "basic_hello_world",
        "timestamp": datetime.now().isoformat()
    }
    
    # Invoke Lambda function
    response = lambda_client.invoke(
        FunctionName='LambdaHelloWorld',
        Payload=json.dumps(test_event)
    )
    
    # Validate Lambda invoke response
    assert response['StatusCode'] == 200, f"Lambda invocation failed with status: {response['StatusCode']}"
    
    # Parse Lambda response payload
    payload = response['Payload'].read().decode('utf-8')
    lambda_response = json.loads(payload)
    
    # Validate Lambda response structure
    assert 'statusCode' in lambda_response, "Lambda response should contain statusCode"
    assert 'body' in lambda_response, "Lambda response should contain body"
    
    # Validate status code
    assert lambda_response['statusCode'] == 200, f"Expected statusCode 200, got {lambda_response['statusCode']}"
    
    # Parse the body (which is JSON stringified)
    body_data = json.loads(lambda_response['body'])
    
    # Validate message content
    assert 'message' in body_data, "Response body should contain message field"
    expected_message = "Hello World! This is local Run!"
    assert body_data['message'] == expected_message, f"Expected '{expected_message}', got '{body_data['message']}'"
    
    print(f"Lambda response: {{'StatusCode': {response['StatusCode']}, 'Payload': '{payload}'}}")


def test_lambda_custom_message(lambda_client, health_check):
    """
    Test the Lambda function with custom input parameters.
    Note: The current Lambda function doesn't process custom input,
    but we test that it handles various inputs gracefully.
    """
    # Custom test event with various parameters
    test_event = {
        "test_type": "custom_message",
        "custom_field": "test_value",
        "user_name": "TestUser",
        "timestamp": datetime.now().isoformat(),
        "nested_object": {
            "key1": "value1",
            "key2": 123
        }
    }
    
    # Invoke Lambda function
    response = lambda_client.invoke(
        FunctionName='LambdaHelloWorld',
        Payload=json.dumps(test_event)
    )
    
    # Validate Lambda invoke response
    assert response['StatusCode'] == 200, f"Lambda invocation failed with status: {response['StatusCode']}"
    
    # Parse Lambda response payload
    payload = response['Payload'].read().decode('utf-8')
    lambda_response = json.loads(payload)
    
    # Validate Lambda response structure
    assert 'statusCode' in lambda_response, "Lambda response should contain statusCode"
    assert 'body' in lambda_response, "Lambda response should contain body"
    assert lambda_response['statusCode'] == 200, f"Expected statusCode 200, got {lambda_response['statusCode']}"
    
    # Parse the body
    body_data = json.loads(lambda_response['body'])
    
    # The Lambda function should return the same message regardless of input
    # This tests that it handles custom input gracefully
    assert 'message' in body_data, "Response body should contain message field"
    expected_message = "Hello World! This is local Run!"
    assert body_data['message'] == expected_message, f"Lambda should return consistent message regardless of input"
    
    print(f"Lambda response: {{'StatusCode': {response['StatusCode']}, 'Message': '{body_data['message']}', 'Input_Handled': True}}")


def test_lambda_error_handling(lambda_client, health_check):
    """
    Test the Lambda function's behavior with invalid or missing input.
    Validates error responses and proper exception handling.
    """
    # Test scenarios with various edge cases
    test_scenarios = [
        # Empty event
        {},
        # Event with None values
        {"field": None},
        # Event with very large data
        {"large_field": "x" * 1000},
        # Event with special characters
        {"special_chars": "!@#$%^&*()[]{}|;':\",./<>?"},
        # Event with unicode characters
        {"unicode": "Hello 世界 🌍"},
        # Event with boolean and numeric values
        {"boolean": True, "number": 42, "float": 3.14}
    ]
    
    for i, test_event in enumerate(test_scenarios):
        # Add scenario identifier
        test_event_with_id = {
            **test_event,
            "scenario_id": i,
            "timestamp": datetime.now().isoformat()
        }
        
        # Invoke Lambda function
        response = lambda_client.invoke(
            FunctionName='LambdaHelloWorld',
            Payload=json.dumps(test_event_with_id)
        )
        
        # Validate that Lambda handles all scenarios gracefully
        assert response['StatusCode'] == 200, f"Scenario {i} failed with status: {response['StatusCode']}"
        
        # Parse response
        payload = response['Payload'].read().decode('utf-8')
        lambda_response = json.loads(payload)
        
        # Validate consistent response structure
        assert lambda_response['statusCode'] == 200, f"Scenario {i}: Lambda should handle gracefully"
        
        # Parse body and validate message
        body_data = json.loads(lambda_response['body'])
        expected_message = "Hello World! This is local Run!"
        assert body_data['message'] == expected_message, f"Scenario {i}: Consistent message expected"
    
    print(f"Lambda response: {{'StatusCode': 200, 'Scenarios_Tested': {len(test_scenarios)}, 'All_Handled_Gracefully': True}}")


def test_lambda_response_format_validation(lambda_client, health_check):
    """
    Test that the Lambda response format matches API Gateway integration format.
    """
    test_event = {
        "test_type": "format_validation",
        "timestamp": datetime.now().isoformat()
    }
    
    # Invoke Lambda function
    response = lambda_client.invoke(
        FunctionName='LambdaHelloWorld',
        Payload=json.dumps(test_event)
    )
    
    # Validate Lambda invoke response
    assert response['StatusCode'] == 200, f"Lambda invocation failed with status: {response['StatusCode']}"
    
    # Parse Lambda response payload
    payload = response['Payload'].read().decode('utf-8')
    lambda_response = json.loads(payload)
    
    # Validate API Gateway integration format
    required_fields = ['statusCode', 'body']
    for field in required_fields:
        assert field in lambda_response, f"Lambda response missing required field: {field}"
    
    # Validate status code is numeric
    assert isinstance(lambda_response['statusCode'], int), "statusCode should be an integer"
    assert lambda_response['statusCode'] == 200, "statusCode should be 200"
    
    # Validate body is a JSON string
    assert isinstance(lambda_response['body'], str), "body should be a JSON string"
    
    # Validate body can be parsed as JSON
    try:
        body_data = json.loads(lambda_response['body'])
        assert isinstance(body_data, dict), "Parsed body should be a dictionary"
        assert 'message' in body_data, "Body should contain message field"
    except json.JSONDecodeError:
        pytest.fail("Lambda response body is not valid JSON")
    
    # Optional fields validation (headers, isBase64Encoded, etc.)
    optional_fields = ['headers', 'isBase64Encoded', 'multiValueHeaders']
    for field in optional_fields:
        if field in lambda_response:
            print(f"Optional field present: {field}")
    
    print("Lambda response format validation passed - matches API Gateway integration format")


def test_lambda_performance_metrics(lambda_client, health_check):
    """
    Test Lambda function performance and measure execution metrics.
    """
    test_event = {
        "test_type": "performance",
        "timestamp": datetime.now().isoformat()
    }
    
    # Perform multiple invocations to test cold start vs warm start
    execution_times = []
    responses = []
    
    for i in range(3):
        start_time = time.time()
        
        response = lambda_client.invoke(
            FunctionName='LambdaHelloWorld',
            Payload=json.dumps({**test_event, "invocation": i})
        )
        
        end_time = time.time()
        execution_time = int((end_time - start_time) * 1000)  # Convert to milliseconds
        execution_times.append(execution_time)
        
        # Validate each response
        assert response['StatusCode'] == 200, f"Invocation {i+1} failed with status: {response['StatusCode']}"
        
        payload = response['Payload'].read().decode('utf-8')
        lambda_response = json.loads(payload)
        responses.append(lambda_response)
        
        # Small delay between invocations
        if i < 2:
            time.sleep(0.5)
    
    # Analyze performance metrics
    avg_execution_time = sum(execution_times) / len(execution_times)
    min_execution_time = min(execution_times)
    max_execution_time = max(execution_times)
    
    # Performance assertions (reasonable for a simple Hello World function)
    assert avg_execution_time < 5000, f"Average execution time too slow: {avg_execution_time}ms"
    assert min_execution_time < 2000, f"Minimum execution time too slow: {min_execution_time}ms"
    
    # Validate all responses were successful and consistent
    expected_message = "Hello World! This is local Run!"
    for i, lambda_response in enumerate(responses):
        assert lambda_response['statusCode'] == 200, f"Response {i+1} failed"
        body_data = json.loads(lambda_response['body'])
        assert body_data['message'] == expected_message, f"Response {i+1} message inconsistent"
    
    # Check for performance improvement in subsequent calls (warm starts)
    if len(execution_times) >= 3:
        cold_start = execution_times[0]
        warm_start_avg = sum(execution_times[1:]) / len(execution_times[1:])
        performance_improvement = cold_start > warm_start_avg
        
        print(f"Performance metrics:")
        print(f"  Cold start: {cold_start}ms")
        print(f"  Warm start average: {int(warm_start_avg)}ms")
        print(f"  Performance improvement: {performance_improvement}")
    
    print(f"Performance test completed: avg={int(avg_execution_time)}ms, min={min_execution_time}ms, max={max_execution_time}ms")


def test_lambda_concurrent_invocations(lambda_client, health_check):
    """
    Test concurrent Lambda invocations to validate thread safety.
    """
    import threading
    import queue
    
    test_event = {
        "test_type": "concurrent",
        "timestamp": datetime.now().isoformat()
    }
    
    results = queue.Queue()
    num_threads = 5
    
    def invoke_lambda(thread_id):
        """Helper function for concurrent Lambda invocations"""
        try:
            start_time = time.time()
            
            response = lambda_client.invoke(
                FunctionName='LambdaHelloWorld',
                Payload=json.dumps({**test_event, "thread_id": thread_id})
            )
            
            end_time = time.time()
            execution_time = int((end_time - start_time) * 1000)
            
            # Parse response
            payload = response['Payload'].read().decode('utf-8')
            lambda_response = json.loads(payload)
            body_data = json.loads(lambda_response['body'])
            
            results.put({
                'thread_id': thread_id,
                'success': response['StatusCode'] == 200 and lambda_response['statusCode'] == 200,
                'execution_time': execution_time,
                'message': body_data.get('message'),
                'lambda_status': response['StatusCode']
            })
            
        except Exception as e:
            results.put({
                'thread_id': thread_id,
                'success': False,
                'error': str(e),
                'execution_time': 0
            })
    
    # Start concurrent threads
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=invoke_lambda, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join(timeout=30)
    
    # Analyze results
    successful_invocations = 0
    total_execution_time = 0
    expected_message = "Hello World! This is local Run!"
    
    while not results.empty():
        result = results.get()
        if result['success']:
            successful_invocations += 1
            total_execution_time += result['execution_time']
            
            # Validate message consistency
            assert result['message'] == expected_message, \
                f"Thread {result['thread_id']} returned inconsistent message: {result['message']}"
        else:
            print(f"Thread {result['thread_id']} failed: {result.get('error', 'Unknown error')}")
    
    success_rate = successful_invocations / num_threads * 100
    avg_execution_time = total_execution_time / successful_invocations if successful_invocations > 0 else 0
    
    # Validate concurrent performance
    assert success_rate >= 90, f"Concurrent execution success rate too low: {success_rate}%"
    assert successful_invocations >= num_threads - 1, f"Too many failed concurrent invocations"
    
    print(f"Concurrent invocations test passed")
    print(f"Results: Success_Rate={success_rate}%, Avg_Execution_Time={int(avg_execution_time)}ms, Successful={successful_invocations}/{num_threads}")


def test_lambda_memory_and_resource_usage(lambda_client, health_check):
    """
    Test Lambda function resource usage and validate efficient execution.
    """
    test_event = {
        "test_type": "resource_usage",
        "timestamp": datetime.now().isoformat()
    }
    
    # Invoke Lambda function
    response = lambda_client.invoke(
        FunctionName='LambdaHelloWorld',
        Payload=json.dumps(test_event)
    )
    
    # Validate basic response
    assert response['StatusCode'] == 200, f"Lambda invocation failed with status: {response['StatusCode']}"
    
    # Parse response
    payload = response['Payload'].read().decode('utf-8')
    lambda_response = json.loads(payload)
    
    # Validate successful execution
    assert lambda_response['statusCode'] == 200, "Lambda function should execute successfully"
    
    body_data = json.loads(lambda_response['body'])
    expected_message = "Hello World! This is local Run!"
    assert body_data['message'] == expected_message, "Message should be consistent"
    
    # Check response metadata for resource information
    response_metadata = response.get('ResponseMetadata', {})
    
    # Log any available metadata
    if response_metadata:
        print(f"Response metadata available: {list(response_metadata.keys())}")
    
    # For a simple Hello World function, the response should be small and efficient
    payload_size = len(payload)
    assert payload_size < 1000, f"Response payload too large for Hello World: {payload_size} bytes"
    
    # Validate response structure efficiency
    assert len(lambda_response) >= 2, "Response should have at least statusCode and body"
    assert len(lambda_response) <= 5, "Response should not have excessive fields for Hello World"
    
    print(f"Resource usage test passed - payload size: {payload_size} bytes, response efficiency validated")


def test_lambda_input_edge_cases(lambda_client, health_check):
    """
    Test Lambda function with various edge case inputs to ensure robustness.
    """
    edge_case_events = [
        # Very large event
        {"large_data": "x" * 10000, "test": "large_input"},
        
        # Event with deeply nested structure
        {"level1": {"level2": {"level3": {"level4": {"message": "deep_nested"}}}}},
        
        # Event with array data
        {"array_field": [1, 2, 3, "string", True, None], "numbers": list(range(100))},
        
        # Event with special data types
        {"timestamp": datetime.now().isoformat(), "boolean": False, "null_field": None},
        
        # Minimal event
        {"minimal": True}
    ]
    
    expected_message = "Hello World! This is local Run!"
    
    for i, test_event in enumerate(edge_case_events):
        # Add scenario identifier
        test_event["edge_case_id"] = i
        
        # Invoke Lambda function
        response = lambda_client.invoke(
            FunctionName='LambdaHelloWorld',
            Payload=json.dumps(test_event)
        )
        
        # Validate that Lambda handles all edge cases gracefully
        assert response['StatusCode'] == 200, f"Edge case {i} failed with status: {response['StatusCode']}"
        
        # Parse and validate response
        payload = response['Payload'].read().decode('utf-8')
        lambda_response = json.loads(payload)
        
        assert lambda_response['statusCode'] == 200, f"Edge case {i}: Lambda should handle gracefully"
        
        body_data = json.loads(lambda_response['body'])
        assert body_data['message'] == expected_message, f"Edge case {i}: Message should be consistent"
    
    print(f"Edge cases test passed - {len(edge_case_events)} scenarios handled gracefully")


def test_lambda_json_serialization(lambda_client, health_check):
    """
    Test that Lambda function properly handles JSON serialization and deserialization.
    """
    # Test with various JSON-serializable data types
    test_event = {
        "string_field": "test string",
        "integer_field": 42,
        "float_field": 3.14159,
        "boolean_field": True,
        "null_field": None,
        "array_field": ["item1", "item2", 3, True],
        "object_field": {
            "nested_string": "nested value",
            "nested_number": 100
        }
    }
    
    # Invoke Lambda function
    response = lambda_client.invoke(
        FunctionName='LambdaHelloWorld',
        Payload=json.dumps(test_event)
    )
    
    # Validate basic response
    assert response['StatusCode'] == 200, f"Lambda invocation failed with status: {response['StatusCode']}"
    
    # Parse and validate JSON response
    payload = response['Payload'].read().decode('utf-8')
    
    # Ensure the payload is valid JSON
    try:
        lambda_response = json.loads(payload)
    except json.JSONDecodeError:
        pytest.fail(f"Lambda response is not valid JSON: {payload}")
    
    # Validate response structure
    assert isinstance(lambda_response, dict), "Lambda response should be a dictionary"
    assert 'statusCode' in lambda_response, "Response should contain statusCode"
    assert 'body' in lambda_response, "Response should contain body"
    
    # Validate body is valid JSON string
    try:
        body_data = json.loads(lambda_response['body'])
        assert isinstance(body_data, dict), "Response body should contain a dictionary"
        assert 'message' in body_data, "Body should contain message field"
    except json.JSONDecodeError:
        pytest.fail("Lambda response body is not valid JSON")
    
    print("JSON serialization test passed - proper JSON handling validated")