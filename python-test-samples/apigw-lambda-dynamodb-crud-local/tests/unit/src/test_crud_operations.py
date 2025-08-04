import pytest
import requests
import json
import time
import docker
import socket
from datetime import datetime


@pytest.fixture(scope="session")
def dynamodb_local():
    """
    Fixture to start DynamoDB Local container.
    Reproduces: docker run --rm -d --network host -p 8000:8000 amazon/dynamodb-local
    """
    client = docker.from_env()
    
    # Check if DynamoDB Local is already running
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        print("DynamoDB Local is already running")
        yield "http://localhost:8000"
        return
    except requests.exceptions.RequestException:
        pass
    
    # Start DynamoDB Local container with port mapping (fixed networking)
    try:
        container = client.containers.run(
            "amazon/dynamodb-local",
            ports={'8000/tcp': 8000},  # Fixed: proper port mapping without host networking
            detach=True,
            remove=True,
            name=f"dynamodb-local-api-test-{int(time.time())}"
        )
        
        # Wait for DynamoDB to be ready
        max_retries = 30
        for i in range(max_retries):
            try:
                response = requests.get("http://localhost:8000", timeout=2)
                if response.status_code == 400:  # DynamoDB returns 400 for root path
                    print("DynamoDB Local container is ready")
                    break
            except requests.exceptions.RequestException:
                time.sleep(1)
                if i == max_retries - 1:
                    container.stop()
                    pytest.fail("DynamoDB Local container failed to start")
        
        yield "http://localhost:8000"
        
        # Cleanup
        try:
            container.stop()
            container.remove()
        except:
            pass
            
    except docker.errors.ImageNotFound:
        pytest.skip("DynamoDB Local Docker image not available")
    except Exception as e:
        pytest.skip(f"Failed to start DynamoDB Local container: {str(e)}")


@pytest.fixture(scope="session")
def sam_local_api(dynamodb_local):
    """
    Fixture to verify SAM Local API Gateway is running.
    Assumes: sam local start-api --docker-network host &
    """
    # Check if SAM Local API Gateway is running on port 3000
    def is_port_open(host, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                result = s.connect_ex((host, port))
                return result == 0
        except:
            return False
    
    max_retries = 10
    for i in range(max_retries):
        if is_port_open("127.0.0.1", 3000):
            try:
                # Try to make a test request to verify API Gateway is responding
                response = requests.get("http://127.0.0.1:3000/init", timeout=10)
                print("SAM Local API Gateway is running and responding")
                break
            except requests.exceptions.RequestException:
                if i == max_retries - 1:
                    pytest.skip("SAM Local API Gateway is not responding. Please start with 'sam local start-api --docker-network host'")
        else:
            if i == max_retries - 1:
                pytest.skip("SAM Local API Gateway is not running on port 3000. Please start with 'sam local start-api --docker-network host'")
        time.sleep(2)
    
    yield "http://127.0.0.1:3000"


@pytest.fixture(scope="session")
def api_client():
    """
    Fixture to create HTTP client for API requests.
    """
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'pytest-api-integration-test'
    })
    return session


def test_01_initialize_table(sam_local_api, api_client, dynamodb_local):
    """
    Test initializing the DynamoDB table (idempotent).
    Reproduces: curl -X GET http://127.0.0.1:3000/init
    
    Based on Lambda init code:
    - Returns 200 with table name when successfully created
    - Returns 500 with error message when table already exists or other error
    """
    base_url = sam_local_api
    
    print("=== Step 1: Initialize DynamoDB Table ===")
    
    # Initialize the DynamoDB table via API Gateway
    response = api_client.get(f"{base_url}/init")
    
    # Handle both success and "already exists" scenarios (idempotent)
    if response.status_code == 200:
        # Table created successfully
        print(f"✓ Table created successfully: {response.status_code}")
        assert 'CRUDLocalTable' in response.text or response.text.strip() == 'CRUDLocalTable', \
            f"Response should contain table name: {response.text}"
        
    elif response.status_code == 500:
        # Check if it's the expected "table already exists" error
        error_text = response.text.lower()
        if any(phrase in error_text for phrase in ['already exists', 'preexisting', 'resourceinuse', 'cannot create']):
            print(f"✓ Table already exists (expected): {response.status_code}")
        else:
            pytest.fail(f"Unexpected 500 error: {response.text}")
            
    else:
        pytest.fail(f"Unexpected response status {response.status_code}: {response.text}")
    
    print(f"Response: {response.text}")
    print()


def test_02_create_item(sam_local_api, api_client):
    """
    Test creating an item.
    Reproduces: curl -X POST http://127.0.0.1:3000/create \
                 -H 'Content-Type: application/json' \
                 -d '{"Id": "123", "name": "Batman"}'
    """
    base_url = sam_local_api
    
    print("=== Step 2: Create Initial Item ===")
    
    # Create test data (exact same as README)
    item_data = {"Id": "123", "name": "Batman"}
    
    # Make POST request to create endpoint
    response = api_client.post(f"{base_url}/create", json=item_data)
    
    # Validate response
    assert response.status_code == 200, f"Create request failed with status {response.status_code}: {response.text}"
    
    # Check response indicates success
    response_text = response.text.lower()
    assert 'added' in response_text or 'created' in response_text or 'success' in response_text or 'item' in response_text, \
        f"Response should indicate item creation: {response.text}"
    
    print(f"✓ Item creation successful: {response.status_code}")
    print(f"Created item: {item_data}")
    print(f"Response: {response.text}")
    print()


def test_03_read_item(sam_local_api, api_client):
    """
    Test reading an item.
    Reproduces: curl -X GET http://127.0.0.1:3000/read \
                 -H 'Content-Type: application/json' \
                 -d '{"Id": "123"}'
    """
    base_url = sam_local_api
    
    print("=== Step 3: Read Item ===")
    
    # Read the item created in previous test (exact same as README)
    read_data = {"Id": "123"}
    
    # Make GET request with JSON body (reproducing curl with -d)
    response = api_client.get(f"{base_url}/read", json=read_data)
    
    # Validate response
    assert response.status_code == 200, f"Read request failed with status {response.status_code}: {response.text}"
    
    # Try to parse JSON response to verify item data
    try:
        response_json = response.json()
        
        # Handle different response formats from Lambda
        item_data = None
        if isinstance(response_json, dict):
            if 'Item' in response_json:
                item_data = response_json['Item']
            elif 'Id' in response_json:
                item_data = response_json
            elif 'response' in response_json and 'Item' in response_json['response']:
                item_data = response_json['response']['Item']
        
        # Validate item data
        if item_data:
            # Handle DynamoDB format (with type descriptors) vs regular format
            item_id = item_data.get('Id')
            item_name = item_data.get('name')
            
            # Handle DynamoDB typed format like {"S": "value"}
            if isinstance(item_id, dict) and 'S' in item_id:
                item_id = item_id['S']
            if isinstance(item_name, dict) and 'S' in item_name:
                item_name = item_name['S']
            
            assert item_id == "123", f"Expected Id '123', got '{item_id}'"
            assert item_name == "Batman", f"Expected name 'Batman', got '{item_name}'"
            
            print(f"✓ Item read successful: Id={item_id}, name={item_name}")
        else:
            # If we can't parse the structure, at least verify the data is present
            response_text = response.text
            assert '123' in response_text and 'Batman' in response_text, \
                f"Response should contain item data: {response.text}"
            print(f"✓ Item read successful (contains expected data)")
            
    except (json.JSONDecodeError, KeyError):
        # If JSON parsing fails, check for text indicators
        response_text = response.text
        assert '123' in response_text and 'Batman' in response_text, \
            f"Response should contain item data: {response.text}"
        print(f"✓ Item read successful (text contains data)")
    
    print(f"Response: {response.text}")
    print()


def test_04_update_item(sam_local_api, api_client):
    """
    Test updating an item.
    Reproduces: curl -X POST http://127.0.0.1:3000/update \
                 -H 'Content-Type: application/json' \
                 -d '{"Id": "123", "name": "Robin"}'
    """
    base_url = sam_local_api
    
    print("=== Step 4: Update Item ===")
    
    # Update the item (exact same as README)
    update_data = {"Id": "123", "name": "Robin"}
    
    # Make POST request to update endpoint
    response = api_client.post(f"{base_url}/update", json=update_data)
    
    # Validate response
    assert response.status_code == 200, f"Update request failed with status {response.status_code}: {response.text}"
    
    # Check response indicates success
    response_text = response.text.lower()
    assert 'updated' in response_text or 'success' in response_text or 'modified' in response_text, \
        f"Response should indicate item update: {response.text}"
    
    print(f"✓ Item update successful: {response.status_code}")
    print(f"Updated to: {update_data}")
    print(f"Response: {response.text}")
    print()


def test_05_check_updated_item(sam_local_api, api_client):
    """
    Test reading the updated item.
    Reproduces: curl -X GET http://127.0.0.1:3000/read \
                 -H 'Content-Type: application/json' \
                 -d '{"Id": "123"}'
    """
    base_url = sam_local_api
    
    print("=== Step 5: Check Updated Item ===")
    
    # Read the updated item (same call as step 3)
    read_data = {"Id": "123"}
    
    # Make GET request with JSON body
    response = api_client.get(f"{base_url}/read", json=read_data)
    
    # Validate response
    assert response.status_code == 200, f"Read updated item failed with status {response.status_code}: {response.text}"
    
    # Try to verify the item was updated to "Robin"
    try:
        response_json = response.json()
        
        # Handle different response formats
        item_data = None
        if isinstance(response_json, dict):
            if 'Item' in response_json:
                item_data = response_json['Item']
            elif 'Id' in response_json:
                item_data = response_json
            elif 'response' in response_json and 'Item' in response_json['response']:
                item_data = response_json['response']['Item']
        
        # Validate updated item data
        if item_data:
            item_name = item_data.get('name')
            
            # Handle DynamoDB typed format
            if isinstance(item_name, dict) and 'S' in item_name:
                item_name = item_name['S']
            
            assert item_name == "Robin", f"Expected updated name 'Robin', got '{item_name}'"
            print(f"✓ Updated item read successful: name={item_name}")
        else:
            # Fallback verification
            response_text = response.text
            assert 'Robin' in response_text, f"Response should contain updated name 'Robin': {response.text}"
            print(f"✓ Updated item read successful (contains 'Robin')")
            
    except (json.JSONDecodeError, KeyError):
        # Fallback verification
        response_text = response.text
        assert 'Robin' in response_text, f"Response should contain updated name 'Robin': {response.text}"
        print(f"✓ Updated item read successful (text contains 'Robin')")
    
    print(f"Response: {response.text}")
    print()


def test_06_delete_item(sam_local_api, api_client):
    """
    Test deleting an item.
    Reproduces: curl -X GET http://127.0.0.1:3000/delete \
                 -H 'Content-Type: application/json' \
                 -d '{"Id": "123"}'
    """
    base_url = sam_local_api
    
    print("=== Step 6: Delete Item ===")
    
    # Delete the item (exact same as README)
    delete_data = {"Id": "123"}
    
    # Make GET request with JSON body to delete endpoint
    response = api_client.get(f"{base_url}/delete", json=delete_data)
    
    # Validate response
    assert response.status_code == 200, f"Delete request failed with status {response.status_code}: {response.text}"
    
    # Check response indicates success
    response_text = response.text.lower()
    assert 'deleted' in response_text or 'success' in response_text or 'removed' in response_text, \
        f"Response should indicate item deletion: {response.text}"
    
    print(f"✓ Item deletion successful: {response.status_code}")
    print(f"Deleted item: {delete_data}")
    print(f"Response: {response.text}")
    print()


def test_07_verify_item_deleted(sam_local_api, api_client):
    """
    Test that the item no longer exists.
    Reproduces: curl -X GET http://127.0.0.1:3000/read \
                 -H 'Content-Type: application/json' \
                 -d '{"Id": "123"}'
    """
    base_url = sam_local_api
    
    print("=== Step 7: Verify Item Deleted ===")
    
    # Try to read the deleted item (same call as step 3 and 5)
    read_data = {"Id": "123"}
    
    # Make GET request with JSON body
    response = api_client.get(f"{base_url}/read", json=read_data)
    
    # Item should not be found - could be 404 or 200 with empty result
    if response.status_code == 404:
        print(f"✓ Item correctly deleted: {response.status_code} Not Found")
    elif response.status_code == 200:
        # Check if response indicates item not found
        try:
            response_json = response.json()
            
            # Verify no item data is returned
            if isinstance(response_json, dict):
                # Handle different response structures
                item_found = False
                if 'Item' in response_json and response_json['Item']:
                    item_found = True
                elif 'response' in response_json and response_json['response'].get('Item'):
                    item_found = True
                elif 'Id' in response_json and response_json['Id'] == '123':
                    item_found = True
                
                assert not item_found, f"Item should be deleted but was found: {response_json}"
            
            print(f"✓ Item correctly deleted: {response.status_code} with empty result")
            
        except json.JSONDecodeError:
            # If response is not JSON, check for text indicators
            response_text = response.text.lower()
            assert 'not found' in response_text or 'empty' in response_text or len(response.text) < 50, \
                f"Response should indicate item not found: {response.text}"
            print(f"✓ Item correctly deleted: text response indicates not found")
    else:
        pytest.fail(f"Unexpected response status for deleted item: {response.status_code}: {response.text}")
    
    print(f"Response: {response.text}")
    print()
    print("=== CRUD Sequence Complete! ===")


def test_08_complete_integration_cycle(sam_local_api, api_client):
    """
    Test a complete CRUD cycle with a new item to verify full integration.
    This test demonstrates the complete workflow in a single test.
    """
    base_url = sam_local_api
    test_id = "integration-456"
    
    print("=== Complete Integration Cycle Test ===")
    print(f"Testing with ID: {test_id}")
    
    # Step 1: Create
    print("Step 1: Create item")
    create_data = {"Id": test_id, "name": "Superman", "city": "Metropolis"}
    create_response = api_client.post(f"{base_url}/create", json=create_data)
    assert create_response.status_code == 200, f"Create failed: {create_response.text}"
    print(f"✓ Create: {create_response.status_code}")
    
    time.sleep(0.5)  # Small delay for consistency
    
    # Step 2: Read
    print("Step 2: Read item")
    read_data = {"Id": test_id}
    read_response = api_client.get(f"{base_url}/read", json=read_data)
    assert read_response.status_code == 200, f"Read failed: {read_response.text}"
    assert test_id in read_response.text, f"Created item not found: {read_response.text}"
    print(f"✓ Read: {read_response.status_code}")
    
    time.sleep(0.5)
    
    # Step 3: Update
    print("Step 3: Update item")
    update_data = {"Id": test_id, "name": "Clark Kent", "city": "Smallville"}
    update_response = api_client.post(f"{base_url}/update", json=update_data)
    assert update_response.status_code == 200, f"Update failed: {update_response.text}"
    print(f"✓ Update: {update_response.status_code}")
    
    time.sleep(0.5)
    
    # Step 4: Verify Update
    print("Step 4: Verify update")
    verify_response = api_client.get(f"{base_url}/read", json=read_data)
    assert verify_response.status_code == 200, f"Verify failed: {verify_response.text}"
    assert "Clark Kent" in verify_response.text, f"Updated name not found: {verify_response.text}"
    print(f"✓ Verify: {verify_response.status_code}")
    
    time.sleep(0.5)
    
    # Step 5: Delete
    print("Step 5: Delete item")
    delete_response = api_client.get(f"{base_url}/delete", json=read_data)
    assert delete_response.status_code == 200, f"Delete failed: {delete_response.text}"
    print(f"✓ Delete: {delete_response.status_code}")
    
    time.sleep(0.5)
    
    # Step 6: Verify Deletion
    print("Step 6: Verify deletion")
    final_response = api_client.get(f"{base_url}/read", json=read_data)
    # Should be 404 or 200 with no item
    if final_response.status_code == 200:
        try:
            final_json = final_response.json()
            # Handle different response structures for empty results
            item_found = False
            if isinstance(final_json, dict):
                if 'Item' in final_json and final_json['Item']:
                    item_found = True
                elif 'response' in final_json and final_json['response'].get('Item'):
                    item_found = True
                elif 'Id' in final_json and final_json['Id'] == test_id:
                    item_found = True
            
            assert not item_found, "Item should be deleted"
        except json.JSONDecodeError:
            assert len(final_response.text) < 100, "Response should be minimal for deleted item"
    print(f"✓ Verify deletion: {final_response.status_code}")
    
    print("✓ Complete integration cycle passed!")
    print()


def test_09_error_scenarios(sam_local_api, api_client):
    """
    Test error scenarios through the API Gateway integration.
    """
    base_url = sam_local_api
    
    print("=== Error Scenarios Test ===")
    
    # Test 1: Read non-existent item
    print("Test 1: Read non-existent item")
    read_nonexistent = api_client.get(f"{base_url}/read", json={"Id": "nonexistent-999"})
    assert read_nonexistent.status_code in [200, 404], \
        f"Reading nonexistent item should return 200 or 404, got {read_nonexistent.status_code}"
    print(f"✓ Read nonexistent: {read_nonexistent.status_code}")
    
    # Test 2: Update non-existent item 
    print("Test 2: Update non-existent item")
    update_nonexistent = api_client.post(f"{base_url}/update", json={"Id": "nonexistent-update", "name": "Ghost"})
    assert update_nonexistent.status_code in [200, 404, 400], \
        f"Update nonexistent should return 200, 404, or 400, got {update_nonexistent.status_code}"
    print(f"✓ Update nonexistent: {update_nonexistent.status_code}")
    
    # Test 3: Delete non-existent item
    print("Test 3: Delete non-existent item") 
    delete_nonexistent = api_client.get(f"{base_url}/delete", json={"Id": "nonexistent-delete"})
    assert delete_nonexistent.status_code == 200, \
        f"Delete nonexistent should succeed (idempotent), got {delete_nonexistent.status_code}"
    print(f"✓ Delete nonexistent: {delete_nonexistent.status_code}")
    
    print("✓ Error scenarios completed")
    print()


def test_10_performance_check(sam_local_api, api_client):
    """
    Test performance characteristics of the API integration.
    """
    base_url = sam_local_api
    
    print("=== Performance Check ===")
    
    # Test response times for different operations
    operations = []
    
    # Test create performance
    start_time = time.time()
    create_response = api_client.post(f"{base_url}/create", json={"Id": "perf-test", "name": "Performance"})
    create_time = time.time() - start_time
    operations.append(('Create', create_time * 1000, create_response.status_code))
    assert create_response.status_code == 200, f"Create failed: {create_response.status_code}"
    
    time.sleep(0.1)
    
    # Test read performance
    start_time = time.time()
    read_response = api_client.get(f"{base_url}/read", json={"Id": "perf-test"})
    read_time = time.time() - start_time
    operations.append(('Read', read_time * 1000, read_response.status_code))
    assert read_response.status_code == 200, f"Read failed: {read_response.status_code}"
    
    time.sleep(0.1)
    
    # Test update performance
    start_time = time.time()
    update_response = api_client.post(f"{base_url}/update", json={"Id": "perf-test", "name": "Updated"})
    update_time = time.time() - start_time
    operations.append(('Update', update_time * 1000, update_response.status_code))
    assert update_response.status_code == 200, f"Update failed: {update_response.status_code}"
    
    time.sleep(0.1)
    
    # Test delete performance
    start_time = time.time()
    delete_response = api_client.get(f"{base_url}/delete", json={"Id": "perf-test"})
    delete_time = time.time() - start_time
    operations.append(('Delete', delete_time * 1000, delete_response.status_code))
    assert delete_response.status_code == 200, f"Delete failed: {delete_response.status_code}"
    
    # Report performance results
    for op_name, op_time, status_code in operations:
        assert op_time < 10000, f"{op_name} operation took too long: {op_time:.0f}ms"
        print(f"✓ {op_name}: {op_time:.0f}ms (status: {status_code})")
    
    avg_time = sum(op[1] for op in operations) / len(operations)
    print(f"✓ Average operation time: {avg_time:.0f}ms")
    
    print("✓ Performance check completed")
    print()