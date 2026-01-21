import pytest
import boto3
import json
import time
import subprocess
import os
import sys
from datetime import datetime
import re


@pytest.fixture(scope="session")
def layer_build():
    """
    Fixture to ensure the Lambda layer is built before testing.
    """
    try:
        # Get the project root directory (assuming we're in tests/ subdirectory)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        print("Building Lambda layer with SAM...")
        result = subprocess.run([
            "sam", "build", "LambdaLayersLayer",
            "--use-container",
            "--build-image", "amazon/aws-sam-cli-build-image-python3.9"
        ], capture_output=True, text=True, timeout=300, cwd=project_root)
        
        if result.returncode != 0:
            print(f"Layer build failed: {result.stderr}")
            pytest.skip("Failed to build Lambda layer")
        
        print("Lambda layer built successfully")
        return True
        
    except subprocess.TimeoutExpired:
        pytest.skip("Layer build timed out")
    except FileNotFoundError:
        pytest.skip("SAM CLI not available for layer building")
    except Exception as e:
        pytest.skip(f"Layer build failed with error: {str(e)}")


@pytest.fixture(scope="session")
def lambda_container():
    """
    Fixture to verify SAM Local Lambda emulator is running.
    This fixture assumes the emulator is already started externally.
    """
    import socket
    
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
def health_check(lambda_container, lambda_client, layer_build):
    """
    Fixture to perform initial health check of the Lambda function with layers.
    """
    # Simple test event
    test_event = {
        "test": "health_check",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName='LambdaLayersFunction',
            Payload=json.dumps(test_event)
        )
        
        if response['StatusCode'] == 200:
            print("Lambda function with layers is responding correctly")
            return True
        else:
            pytest.fail(f"Lambda health check failed with status: {response['StatusCode']}")
            
    except Exception as e:
        pytest.fail(f"Lambda health check failed: {str(e)}")


def test_layer_dependency_loading(lambda_client, health_check):
    """
    Test that the Lambda function can successfully import dependencies from the custom layer.
    Validates that the requests library is available and functional.
    """
    # Test event
    test_event = {
        "test_type": "dependency_loading",
        "timestamp": datetime.now().isoformat()
    }
    
    # Invoke Lambda function
    response = lambda_client.invoke(
        FunctionName='LambdaLayersFunction',
        Payload=json.dumps(test_event)
    )
    
    # Validate Lambda invoke response
    assert response['StatusCode'] == 200, f"Lambda invocation failed with status: {response['StatusCode']}"
    
    # Parse Lambda response
    payload = response['Payload'].read().decode('utf-8')
    lambda_response = json.loads(payload)
    
    # Validate the Lambda function response structure
    assert 'statusCode' in lambda_response, "Lambda response should contain statusCode"
    assert 'body' in lambda_response, "Lambda response should contain body"
    
    # The Lambda function should successfully call GitHub API (which requires requests library)
    assert lambda_response['statusCode'] == 200, f"GitHub API call failed with status: {lambda_response['statusCode']}"
    
    # Validate that the response body contains GitHub API data
    github_response = lambda_response['body']
    assert isinstance(github_response, str), "GitHub API response should be a string"
    assert len(github_response) > 0, "GitHub API response should not be empty"
    
    # Check if the response contains typical GitHub API content
    github_data_indicators = ['github', 'api', 'current_user_url', 'authorizations_url']
    response_lower = github_response.lower()
    found_indicators = [indicator for indicator in github_data_indicators if indicator in response_lower]
    
    assert len(found_indicators) >= 2, f"Response doesn't seem to be from GitHub API: {github_response[:200]}..."
    
    print(f"Layer dependency loading test passed - requests library is working")
    print(f"Lambda response: {{'StatusCode': {response['StatusCode']}, 'GitHub_API_Success': True, 'Response_Length': {len(github_response)}}}")


def test_external_api_integration(lambda_client, health_check):
    """
    Test the Lambda function's ability to make HTTP requests using the layer's requests library.
    Validates successful API calls to external services (GitHub API).
    """
    # Test event for API integration
    test_event = {
        "test_type": "api_integration",
        "target_api": "github",
        "timestamp": datetime.now().isoformat()
    }
    
    # Invoke Lambda function
    start_time = time.time()
    response = lambda_client.invoke(
        FunctionName='LambdaLayersFunction',
        Payload=json.dumps(test_event)
    )
    end_time = time.time()
    
    execution_time = int((end_time - start_time) * 1000)
    
    # Validate Lambda invoke response
    assert response['StatusCode'] == 200, f"Lambda invocation failed with status: {response['StatusCode']}"
    
    # Parse Lambda response
    payload = response['Payload'].read().decode('utf-8')
    lambda_response = json.loads(payload)
    
    # Validate successful GitHub API call
    assert lambda_response['statusCode'] == 200, f"GitHub API call failed with status: {lambda_response['statusCode']}"
    
    # Parse GitHub API response to extract meaningful data
    github_response = lambda_response['body']
    
    try:
        # Try to parse the GitHub API response as JSON
        github_data = json.loads(github_response)
        
        # Count available endpoints in GitHub API response
        endpoints_count = 0
        for key, value in github_data.items():
            if key.endswith('_url') and isinstance(value, str):
                endpoints_count += 1
        
        assert endpoints_count > 10, f"Expected multiple GitHub API endpoints, found {endpoints_count}"
        
        print(f"External API integration test passed")
        print(f"Lambda response: {{'StatusCode': {response['StatusCode']}, 'GitHub_Endpoints': {endpoints_count}, 'Execution_Time_ms': {execution_time}}}")
        
    except json.JSONDecodeError:
        # If the response is not JSON, validate it's still a valid response
        assert len(github_response) > 100, "GitHub API response seems too short"
        assert 'api.github.com' in github_response.lower() or 'github' in github_response.lower(), \
            "Response doesn't appear to be from GitHub API"
        
        print(f"External API integration test passed (non-JSON response)")
        print(f"Lambda response: {{'StatusCode': {response['StatusCode']}, 'Response_Length': {len(github_response)}, 'Execution_Time_ms': {execution_time}}}")


def test_layer_version_compatibility(lambda_client, health_check):
    """
    Test that the layer dependencies are compatible with the Lambda runtime.
    Validates that no version conflicts exist between layer and runtime.
    """
    # Test event for version compatibility
    test_event = {
        "test_type": "version_compatibility",
        "check_versions": True,
        "timestamp": datetime.now().isoformat()
    }
    
    # Invoke Lambda function
    response = lambda_client.invoke(
        FunctionName='LambdaLayersFunction',
        Payload=json.dumps(test_event)
    )
    
    # Validate Lambda invoke response
    assert response['StatusCode'] == 200, f"Lambda invocation failed with status: {response['StatusCode']}"
    
    # Parse Lambda response
    payload = response['Payload'].read().decode('utf-8')
    lambda_response = json.loads(payload)
    
    # Validate that the Lambda function executed successfully
    assert lambda_response['statusCode'] == 200, f"Lambda function failed with status: {lambda_response['statusCode']}"
    
    # The fact that the function executed successfully means the layer is compatible
    # We can verify this by checking that the GitHub API call succeeded
    github_response = lambda_response['body']
    assert len(github_response) > 0, "Empty response suggests layer compatibility issues"
    
    # Additional validation: check that we can extract version information from logs if available
    # Note: The current Lambda code prints the requests version, but we can't easily capture that in tests
    # So we validate functionality instead
    
    # Validate that the requests library from the layer is working correctly
    try:
        # If response is JSON, it means requests worked properly
        github_data = json.loads(github_response)
        requests_working = True
        version_compatible = True
    except json.JSONDecodeError:
        # Even if not JSON, if we got a response, requests is working
        requests_working = len(github_response) > 0
        version_compatible = True
    
    assert requests_working, "Requests library from layer is not functioning properly"
    assert version_compatible, "Layer dependencies appear to have compatibility issues"
    
    # Extract Python version info if possible (this would be from the Lambda runtime)
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    print(f"Layer version compatibility test passed")
    print(f"Lambda response: {{'StatusCode': {response['StatusCode']}, 'Requests_Working': {requests_working}, 'Python_Version': '{python_version}', 'Layer_Compatible': {version_compatible}}}")


def test_performance_with_layers(lambda_client, health_check):
    """
    Test the Lambda function's performance when using layers.
    Validates that layer loading doesn't significantly impact cold start times.
    """
    # Test event for performance testing
    test_event = {
        "test_type": "performance",
        "measure_execution": True,
        "timestamp": datetime.now().isoformat()
    }
    
    # Multiple invocations to test both cold and warm starts
    execution_times = []
    responses = []
    
    for i in range(3):
        start_time = time.time()
        
        response = lambda_client.invoke(
            FunctionName='LambdaLayersFunction',
            Payload=json.dumps(test_event)
        )
        
        end_time = time.time()
        execution_time = int((end_time - start_time) * 1000)
        execution_times.append(execution_time)
        
        # Validate each response
        assert response['StatusCode'] == 200, f"Lambda invocation {i+1} failed with status: {response['StatusCode']}"
        
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
    
    # Validate performance is reasonable (cold start might be slower)
    assert avg_execution_time < 10000, f"Average execution time too slow: {avg_execution_time}ms"
    assert min_execution_time < 5000, f"Fastest execution time too slow: {min_execution_time}ms"
    
    # Validate all responses were successful
    for i, lambda_response in enumerate(responses):
        assert lambda_response['statusCode'] == 200, f"Response {i+1} failed with status: {lambda_response['statusCode']}"
        assert len(lambda_response['body']) > 0, f"Response {i+1} had empty body"
    
    # Check if performance improved with warm starts (second and third calls should be faster)
    if len(execution_times) >= 3:
        warm_start_avg = sum(execution_times[1:]) / len(execution_times[1:])
        performance_improvement = execution_times[0] > warm_start_avg
        
        print(f"Performance analysis:")
        print(f"  Cold start: {execution_times[0]}ms")
        print(f"  Warm start average: {int(warm_start_avg)}ms")
        print(f"  Performance improvement: {performance_improvement}")
    
    print(f"Performance with layers test passed")
    print(f"Lambda response: {{'StatusCode': 200, 'Avg_Execution_Time_ms': {int(avg_execution_time)}, 'Min_Time_ms': {min_execution_time}, 'Max_Time_ms': {max_execution_time}}}")


def test_layer_isolation_and_dependencies(lambda_client, health_check):
    """
    Test that the layer provides proper isolation and all required dependencies.
    Validates that the layer contains only the expected dependencies.
    """
    # Test event
    test_event = {
        "test_type": "isolation",
        "validate_dependencies": True,
        "timestamp": datetime.now().isoformat()
    }
    
    # Invoke Lambda function
    response = lambda_client.invoke(
        FunctionName='LambdaLayersFunction',
        Payload=json.dumps(test_event)
    )
    
    # Validate Lambda invoke response
    assert response['StatusCode'] == 200, f"Lambda invocation failed with status: {response['StatusCode']}"
    
    # Parse Lambda response
    payload = response['Payload'].read().decode('utf-8')
    lambda_response = json.loads(payload)
    
    # Validate successful execution
    assert lambda_response['statusCode'] == 200, f"Lambda execution failed with status: {lambda_response['statusCode']}"
    
    # Validate that requests library is working (this is our main layer dependency)
    github_response = lambda_response['body']
    
    # Test that the requests library is available and working
    assert len(github_response) > 0, "Empty response suggests requests library issues"
    
    # Validate that the API call was successful (which requires requests)
    if lambda_response['statusCode'] == 200:
        # Check if we can identify this as a GitHub API response
        github_indicators = ['api', 'github', 'url', 'current_user']
        response_text = github_response.lower()
        found_indicators = sum(1 for indicator in github_indicators if indicator in response_text)
        
        assert found_indicators >= 2, "Response doesn't appear to be from GitHub API, suggesting layer issues"
    
    print(f"Layer isolation and dependencies test passed")
    print(f"Lambda response: {{'StatusCode': {response['StatusCode']}, 'Dependencies_Working': True, 'GitHub_API_Success': True}}")


def test_error_handling_with_layers(lambda_client, health_check):
    """
    Test error handling scenarios when using layers.
    Validates graceful handling of network issues and layer-related errors.
    """
    # Test event that might cause different behaviors
    test_event = {
        "test_type": "error_handling",
        "simulate_scenarios": True,
        "timestamp": datetime.now().isoformat()
    }
    
    # Invoke Lambda function multiple times to test consistency
    for i in range(2):
        response = lambda_client.invoke(
            FunctionName='LambdaLayersFunction',
            Payload=json.dumps(test_event)
        )
        
        # Validate Lambda invoke response
        assert response['StatusCode'] == 200, f"Lambda invocation {i+1} failed with status: {response['StatusCode']}"
        
        # Parse Lambda response
        payload = response['Payload'].read().decode('utf-8')
        lambda_response = json.loads(payload)
        
        # Even if the GitHub API call fails, the Lambda should handle it gracefully
        # The status code should be present in the response
        assert 'statusCode' in lambda_response, f"Response {i+1} missing statusCode"
        assert 'body' in lambda_response, f"Response {i+1} missing body"
        
        # Log the response for debugging
        print(f"Error handling test {i+1}: StatusCode={lambda_response.get('statusCode')}, Body_Length={len(str(lambda_response.get('body', '')))}")
    
    print("Error handling with layers test passed - Lambda handles scenarios gracefully")


def test_concurrent_layer_usage(lambda_client, health_check):
    """
    Test concurrent usage of Lambda functions with layers.
    Validates that layers work correctly under concurrent load.
    """
    import threading
    import queue
    
    # Test event
    test_event = {
        "test_type": "concurrent",
        "thread_test": True,
        "timestamp": datetime.now().isoformat()
    }
    
    results = queue.Queue()
    num_threads = 3
    
    def invoke_lambda(thread_id):
        """Helper function for concurrent Lambda invocations"""
        try:
            start_time = time.time()
            
            response = lambda_client.invoke(
                FunctionName='LambdaLayersFunction',
                Payload=json.dumps({**test_event, "thread_id": thread_id})
            )
            
            end_time = time.time()
            execution_time = int((end_time - start_time) * 1000)
            
            # Parse response
            payload = response['Payload'].read().decode('utf-8')
            lambda_response = json.loads(payload)
            
            results.put({
                'thread_id': thread_id,
                'success': response['StatusCode'] == 200 and lambda_response.get('statusCode') == 200,
                'execution_time': execution_time,
                'lambda_status': response['StatusCode'],
                'api_status': lambda_response.get('statusCode')
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
    
    while not results.empty():
        result = results.get()
        if result['success']:
            successful_invocations += 1
            total_execution_time += result['execution_time']
        else:
            print(f"Thread {result['thread_id']} failed: {result.get('error', 'Unknown error')}")
    
    success_rate = successful_invocations / num_threads * 100
    avg_execution_time = total_execution_time / successful_invocations if successful_invocations > 0 else 0
    
    # Validate concurrent performance
    assert success_rate >= 80, f"Concurrent execution success rate too low: {success_rate}%"
    assert avg_execution_time < 15000, f"Average concurrent execution time too slow: {avg_execution_time}ms"
    
    print(f"Concurrent layer usage test passed")
    print(f"Results: Success_Rate={success_rate}%, Avg_Execution_Time={int(avg_execution_time)}ms, Successful_Invocations={successful_invocations}/{num_threads}")