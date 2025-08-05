import pytest
import requests
import json
import time
import socket
import threading
import queue
from datetime import datetime
from requests.exceptions import RequestException, ConnectionError


@pytest.fixture(scope="session")
def api_container():
    """
    Fixture to verify SAM Local API Gateway emulator is running.
    This fixture assumes the emulator is already started externally.
    """
    # Check if API Gateway emulator is running on port 3000
    def is_port_open(host, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                result = s.connect_ex((host, port))
                return result == 0
        except:
            return False
    
    if not is_port_open("127.0.0.1", 3000):
        pytest.skip("SAM Local API Gateway emulator is not running on port 3000. Please start with 'sam local start-api --port 3000'")
    
    print("SAM Local API Gateway is running on port 3000")
    yield "http://127.0.0.1:3000"


@pytest.fixture(scope="session")
def api_client():
    """
    Fixture to create a base URL for API testing.
    """
    return "http://127.0.0.1:3000"


@pytest.fixture(scope="session")
def health_check(api_container, api_client):
    """
    Fixture to perform initial health check of the API Gateway endpoint.
    """
    try:
        response = requests.get(f"{api_client}/MOCK", timeout=10)
        
        if response.status_code == 200:
            print("API Gateway endpoint is responding correctly")
            return True
        else:
            pytest.fail(f"API Gateway health check failed with status: {response.status_code}")
            
    except Exception as e:
        pytest.fail(f"API Gateway health check failed: {str(e)}")


def test_api_basic_mock_response(api_client, health_check):
    """
    Test the basic API Gateway mock endpoint.
    Validates the default mock response functionality.
    """
    # Make GET request to mock endpoint
    start_time = time.time()
    response = requests.get(f"{api_client}/MOCK", timeout=10)
    end_time = time.time()
    
    response_time = int((end_time - start_time) * 1000)
    
    # Validate HTTP response
    assert response.status_code == 200, f"API request failed with status: {response.status_code}"
    
    # Validate response headers
    assert 'content-type' in response.headers, "Response should contain Content-Type header"
    content_type = response.headers.get('content-type', '').lower()
    assert 'json' in content_type, f"Expected JSON content type, got: {content_type}"
    
    # Validate response content
    try:
        response_data = response.json()
    except ValueError:
        pytest.fail(f"Response is not valid JSON: {response.text}")
    
    # Validate mock response content
    expected_response = "This is mock response"
    assert response_data == expected_response, f"Expected '{expected_response}', got '{response_data}'"
    
    # Validate response time is reasonable
    assert response_time < 5000, f"Response time too slow: {response_time}ms"
    
    print(f"API Gateway response: {{'StatusCode': {response.status_code}, 'Response': '{response_data}', 'ResponseTime': {response_time}ms}}")


def test_api_response_format_validation(api_client, health_check):
    """
    Test that the API Gateway response format is correct.
    Validates headers, content type, and JSON structure.
    """
    # Make request to mock endpoint
    response = requests.get(f"{api_client}/MOCK", timeout=10)
    
    # Validate HTTP status code
    assert response.status_code == 200, f"API request failed with status: {response.status_code}"
    
    # Validate response headers
    required_headers = ['content-type', 'content-length']
    for header in required_headers:
        assert header in response.headers, f"Response missing required header: {header}"
    
    # Validate content type
    content_type = response.headers.get('content-type', '')
    assert 'application/json' in content_type or 'json' in content_type, \
        f"Expected JSON content type, got: {content_type}"
    
    # Validate content length
    content_length = int(response.headers.get('content-length', 0))
    assert content_length > 0, "Content-Length should be greater than 0"
    
    # Validate response body
    response_text = response.text
    assert len(response_text) > 0, "Response body should not be empty"
    
    # Validate JSON parsing
    try:
        response_data = response.json()
        assert response_data is not None, "Parsed JSON should not be None"
    except ValueError as e:
        pytest.fail(f"Response body is not valid JSON: {e}")
    
    # Validate response encoding
    assert response.encoding is not None, "Response should have encoding information"
    
    print("API Gateway response format validation passed - all headers and format requirements met")


def test_api_error_handling(api_client, health_check):
    """
    Test API Gateway error handling with invalid requests.
    Validates proper error responses for various edge cases.
    """
    # Test scenarios with expected error responses
    test_scenarios = [
        # Invalid endpoint
        {
            "url": f"{api_client}/INVALID",
            "method": "GET",
            "expected_status": [403, 404],
            "description": "Invalid endpoint"
        },
        # Wrong HTTP method
        {
            "url": f"{api_client}/MOCK",
            "method": "POST",
            "expected_status": [403, 405],
            "description": "Wrong HTTP method"
        },
        # Wrong HTTP method - PUT
        {
            "url": f"{api_client}/MOCK",
            "method": "PUT",
            "expected_status": [403, 405],
            "description": "Unsupported HTTP method PUT"
        },
        # Wrong HTTP method - DELETE
        {
            "url": f"{api_client}/MOCK",
            "method": "DELETE",
            "expected_status": [403, 405],
            "description": "Unsupported HTTP method DELETE"
        }
    ]
    
    for scenario in test_scenarios:
        try:
            if scenario["method"] == "GET":
                response = requests.get(scenario["url"], timeout=10)
            elif scenario["method"] == "POST":
                response = requests.post(scenario["url"], timeout=10)
            elif scenario["method"] == "PUT":
                response = requests.put(scenario["url"], timeout=10)
            elif scenario["method"] == "DELETE":
                response = requests.delete(scenario["url"], timeout=10)
            
            # Validate error status codes
            assert response.status_code in scenario["expected_status"], \
                f"{scenario['description']}: Expected status {scenario['expected_status']}, got {response.status_code}"
            
            # Validate that error responses are still properly formatted
            assert 'content-type' in response.headers, f"{scenario['description']}: Error response should have content-type"
            
            print(f"Error handling test passed: {scenario['description']} returned status {response.status_code}")
            
        except requests.RequestException as e:
            # Network errors are acceptable for invalid requests
            print(f"Network error for {scenario['description']}: {str(e)} (acceptable)")
    
    print("API Gateway error handling test passed - all error scenarios handled appropriately")


def test_api_performance_metrics(api_client, health_check):
    """
    Test API Gateway performance and measure response metrics.
    """
    # Perform multiple requests to measure performance consistency
    response_times = []
    responses = []
    
    for i in range(5):
        start_time = time.time()
        
        response = requests.get(f"{api_client}/MOCK", timeout=10)
        
        end_time = time.time()
        response_time = int((end_time - start_time) * 1000)  # Convert to milliseconds
        response_times.append(response_time)
        
        # Validate each response
        assert response.status_code == 200, f"Request {i+1} failed with status: {response.status_code}"
        
        response_data = response.json()
        responses.append(response_data)
        
        # Small delay between requests
        if i < 4:
            time.sleep(0.2)
    
    # Analyze performance metrics
    avg_response_time = sum(response_times) / len(response_times)
    min_response_time = min(response_times)
    max_response_time = max(response_times)
    
    # Performance assertions (reasonable for API Gateway + Lambda)
    assert avg_response_time < 10000, f"Average response time too slow: {avg_response_time}ms"
    assert min_response_time < 5000, f"Minimum response time too slow: {min_response_time}ms"
    
    # Validate response consistency
    expected_response = "This is mock response"
    for i, response_data in enumerate(responses):
        assert response_data == expected_response, f"Response {i+1} inconsistent: {response_data}"
    
    # Check for performance consistency (no response should be significantly slower)
    max_acceptable_time = avg_response_time * 3
    for i, response_time in enumerate(response_times):
        assert response_time < max_acceptable_time, \
            f"Request {i+1} response time ({response_time}ms) significantly slower than average ({avg_response_time}ms)"
    
    print(f"Performance metrics:")
    print(f"  Average: {int(avg_response_time)}ms")
    print(f"  Min: {min_response_time}ms")
    print(f"  Max: {max_response_time}ms")
    print(f"  Consistency: All responses within acceptable range")
    
    print(f"Performance test completed: avg={int(avg_response_time)}ms, min={min_response_time}ms, max={max_response_time}ms")


def test_api_concurrent_requests(api_client, health_check):
    """
    Test concurrent API requests to validate thread safety and load handling.
    """
    results = queue.Queue()
    num_threads = 5
    
    def make_api_request(thread_id):
        """Helper function for concurrent API requests"""
        try:
            start_time = time.time()
            
            response = requests.get(f"{api_client}/MOCK", timeout=15)
            
            end_time = time.time()
            response_time = int((end_time - start_time) * 1000)
            
            # Parse response
            response_data = response.json()
            
            results.put({
                'thread_id': thread_id,
                'success': response.status_code == 200,
                'response_time': response_time,
                'response_data': response_data,
                'status_code': response.status_code
            })
            
        except Exception as e:
            results.put({
                'thread_id': thread_id,
                'success': False,
                'error': str(e),
                'response_time': 0
            })
    
    # Start concurrent threads
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=make_api_request, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join(timeout=30)
    
    # Analyze results
    successful_requests = 0
    total_response_time = 0
    expected_response = "This is mock response"
    
    while not results.empty():
        result = results.get()
        if result['success']:
            successful_requests += 1
            total_response_time += result['response_time']
            
            # Validate response consistency
            assert result['response_data'] == expected_response, \
                f"Thread {result['thread_id']} returned inconsistent response: {result['response_data']}"
        else:
            print(f"Thread {result['thread_id']} failed: {result.get('error', 'Unknown error')}")
    
    success_rate = successful_requests / num_threads * 100
    avg_response_time = total_response_time / successful_requests if successful_requests > 0 else 0
    
    # Validate concurrent performance
    assert success_rate >= 90, f"Concurrent request success rate too low: {success_rate}%"
    assert successful_requests >= num_threads - 1, f"Too many failed concurrent requests"
    assert avg_response_time < 15000, f"Average concurrent response time too slow: {avg_response_time}ms"
    
    print(f"Concurrent requests test passed")
    print(f"Results: Success_Rate={success_rate}%, Avg_Response_Time={int(avg_response_time)}ms, Successful={successful_requests}/{num_threads}")


def test_api_input_validation(api_client, health_check):
    """
    Test API Gateway with various input scenarios and query parameters.
    """
    # Test scenarios with different request variations
    test_scenarios = [
        # Basic request
        {
            "url": f"{api_client}/MOCK",
            "params": None,
            "headers": None,
            "description": "Basic request"
        },
        # Request with query parameters (should still work)
        {
            "url": f"{api_client}/MOCK",
            "params": {"param1": "value1", "param2": "value2"},
            "headers": None,
            "description": "Request with query parameters"
        },
        # Request with custom headers
        {
            "url": f"{api_client}/MOCK",
            "params": None,
            "headers": {"User-Agent": "pytest-test", "X-Custom-Header": "test-value"},
            "description": "Request with custom headers"
        },
        # Request with Accept header
        {
            "url": f"{api_client}/MOCK",
            "params": None,
            "headers": {"Accept": "application/json"},
            "description": "Request with Accept header"
        },
        # Combined request
        {
            "url": f"{api_client}/MOCK",
            "params": {"test": "combined"},
            "headers": {"Accept": "application/json", "X-Test": "true"},
            "description": "Combined request with params and headers"
        }
    ]
    
    expected_response = "This is mock response"
    
    for i, scenario in enumerate(test_scenarios):
        try:
            response = requests.get(
                scenario["url"], 
                params=scenario["params"], 
                headers=scenario["headers"], 
                timeout=10
            )
            
            # Validate basic response
            assert response.status_code == 200, \
                f"{scenario['description']}: Expected status 200, got {response.status_code}"
            
            # Validate response content consistency
            response_data = response.json()
            assert response_data == expected_response, \
                f"{scenario['description']}: Response should be consistent regardless of input"
            
            # Validate response format
            assert 'content-type' in response.headers, \
                f"{scenario['description']}: Response should have content-type header"
            
            print(f"Input validation test {i+1} passed: {scenario['description']}")
            
        except requests.RequestException as e:
            pytest.fail(f"Input validation test failed for {scenario['description']}: {str(e)}")
    
    print(f"Input validation test passed - {len(test_scenarios)} scenarios handled correctly")


def test_api_response_headers_validation(api_client, health_check):
    """
    Test that API Gateway returns appropriate response headers.
    """
    response = requests.get(f"{api_client}/MOCK", timeout=10)
    
    # Validate basic response
    assert response.status_code == 200, f"API request failed with status: {response.status_code}"
    
    # Check for essential headers
    essential_headers = ['content-type', 'content-length']
    for header in essential_headers:
        assert header in response.headers, f"Missing essential header: {header}"
    
    # Validate content-type header
    content_type = response.headers.get('content-type', '').lower()
    valid_content_types = ['application/json', 'text/json', 'json']
    assert any(ct in content_type for ct in valid_content_types), \
        f"Invalid content-type for JSON response: {content_type}"
    
    # Validate content-length header
    content_length = response.headers.get('content-length')
    if content_length:
        assert int(content_length) > 0, "Content-Length should be greater than 0"
        assert int(content_length) == len(response.content), \
            "Content-Length should match actual content length"
    
    # Check for server header (optional but informative)
    server_header = response.headers.get('server', '')
    if server_header:
        print(f"Server header present: {server_header}")
    
    # Validate that headers are properly formatted
    for header_name, header_value in response.headers.items():
        assert isinstance(header_name, str), f"Header name should be string: {header_name}"
        assert isinstance(header_value, str), f"Header value should be string: {header_value}"
        assert len(header_name) > 0, f"Header name should not be empty"
    
    print("Response headers validation passed - all required headers present and properly formatted")


def test_api_timeout_handling(api_client, health_check):
    """
    Test API Gateway timeout handling and response time limits.
    """
    # Test with various timeout scenarios
    timeout_scenarios = [
        {"timeout": 30, "description": "Normal timeout"},
        {"timeout": 10, "description": "Standard timeout"},
        {"timeout": 5, "description": "Short timeout"}
    ]
    
    for scenario in timeout_scenarios:
        try:
            start_time = time.time()
            response = requests.get(f"{api_client}/MOCK", timeout=scenario["timeout"])
            end_time = time.time()
            
            response_time = int((end_time - start_time) * 1000)
            
            # Validate response
            assert response.status_code == 200, \
                f"{scenario['description']}: Request failed with status {response.status_code}"
            
            # Validate response time is within timeout
            timeout_ms = scenario["timeout"] * 1000
            assert response_time < timeout_ms, \
                f"{scenario['description']}: Response time ({response_time}ms) exceeded timeout ({timeout_ms}ms)"
            
            # Validate response content
            response_data = response.json()
            expected_response = "This is mock response"
            assert response_data == expected_response, \
                f"{scenario['description']}: Response content should be consistent"
            
            print(f"Timeout test passed: {scenario['description']} - {response_time}ms")
            
        except requests.Timeout:
            pytest.fail(f"Request timed out for {scenario['description']} - this shouldn't happen for a mock endpoint")
        except requests.RequestException as e:
            pytest.fail(f"Request failed for {scenario['description']}: {str(e)}")
    
    print("Timeout handling test passed - all timeout scenarios handled correctly")


def test_api_connection_resilience(api_client, health_check):
    """
    Test API Gateway connection resilience with rapid sequential requests.
    """
    # Make rapid sequential requests to test connection handling
    num_requests = 10
    successful_requests = 0
    response_times = []
    
    for i in range(num_requests):
        try:
            start_time = time.time()
            response = requests.get(f"{api_client}/MOCK", timeout=10)
            end_time = time.time()
            
            response_time = int((end_time - start_time) * 1000)
            response_times.append(response_time)
            
            if response.status_code == 200:
                successful_requests += 1
                
                # Validate response content
                response_data = response.json()
                expected_response = "This is mock response"
                assert response_data == expected_response, \
                    f"Request {i+1}: Response content inconsistent"
            
            # Very small delay to make rapid requests
            time.sleep(0.05)
            
        except requests.RequestException as e:
            print(f"Request {i+1} failed: {str(e)}")
    
    success_rate = successful_requests / num_requests * 100
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    # Validate connection resilience
    assert success_rate >= 90, f"Connection resilience test failed: success rate {success_rate}%"
    assert successful_requests >= num_requests - 2, f"Too many failed requests: {successful_requests}/{num_requests}"
    
    if response_times:
        assert avg_response_time < 8000, f"Average response time too slow under load: {avg_response_time}ms"
    
    print(f"Connection resilience test passed")
    print(f"Results: Success_Rate={success_rate}%, Avg_Response_Time={int(avg_response_time)}ms, Successful={successful_requests}/{num_requests}")