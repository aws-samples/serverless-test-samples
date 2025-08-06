import pytest
import boto3
import json
import time
import socket
import threading
import queue
import os
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError
from decimal import Decimal


@pytest.fixture(scope="session")
def dynamodb_container():
    """
    Fixture to verify DynamoDB Local container is running.
    This fixture assumes the container is already started externally.
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
        pytest.skip("DynamoDB Local is not running on port 8000. Please start with 'docker run --rm -d --name dynamodb-local --network host -p 8000:8000 amazon/dynamodb-local'")
    
    print("DynamoDB Local is running on port 8000")
    yield "http://127.0.0.1:8000"


@pytest.fixture(scope="session")
def dynamodb_client():
    """
    Fixture to create a DynamoDB client for local testing.
    """
    return boto3.client(
        'dynamodb',
        endpoint_url="http://127.0.0.1:8000",
        region_name='us-east-1',
        aws_access_key_id='dummy',
        aws_secret_access_key='dummy'
    )


@pytest.fixture(scope="session")
def dynamodb_resource():
    """
    Fixture to create a DynamoDB resource for higher-level operations.
    """
    return boto3.resource(
        'dynamodb',
        endpoint_url="http://127.0.0.1:8000",
        region_name='us-east-1',
        aws_access_key_id='dummy',
        aws_secret_access_key='dummy'
    )


@pytest.fixture(scope="function")
def test_table(dynamodb_client, dynamodb_resource):
    """
    Fixture to create and manage a test table for each test function.
    """
    table_name = "CRUDLocalTable"
    
    # Create table
    try:
        dynamodb_client.create_table(
            TableName=table_name,
            AttributeDefinitions=[
                {
                    'AttributeName': 'Id',
                    'AttributeType': 'S'
                }
            ],
            KeySchema=[
                {
                    'AttributeName': 'Id',
                    'KeyType': 'HASH'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Wait for table to be active
        waiter = dynamodb_client.get_waiter('table_exists')
        waiter.wait(TableName=table_name, WaiterConfig={'Delay': 1, 'MaxAttempts': 10})
        
    except ClientError as e:
        if e.response['Error']['Code'] != 'ResourceInUseException':
            raise
    
    # Get table resource
    table = dynamodb_resource.Table(table_name)
    
    yield table
    
    # Cleanup: Delete table after test
    try:
        table.delete()
        waiter = dynamodb_client.get_waiter('table_not_exists')
        waiter.wait(TableName=table_name, WaiterConfig={'Delay': 1, 'MaxAttempts': 10})
    except ClientError:
        pass  # Table might already be deleted


@pytest.fixture(scope="session")
def health_check(dynamodb_container, dynamodb_client):
    """
    Fixture to perform initial health check of DynamoDB Local.
    """
    try:
        # Try to list tables to verify connection
        response = dynamodb_client.list_tables()
        
        print("DynamoDB Local health check passed")
        return True
        
    except Exception as e:
        pytest.fail(f"DynamoDB Local health check failed: {str(e)}")


def test_table_creation_and_setup(dynamodb_client, test_table, health_check):
    """
    Test DynamoDB table creation and basic setup.
    Validates table schema, status, and initial state.
    """
    table_name = test_table.table_name
    
    # Describe the table to get detailed information
    response = dynamodb_client.describe_table(TableName=table_name)
    table_description = response['Table']
    
    # Validate table properties
    assert table_description['TableName'] == table_name
    assert table_description['TableStatus'] == 'ACTIVE'
    assert table_description['KeySchema'][0]['AttributeName'] == 'Id'
    assert table_description['KeySchema'][0]['KeyType'] == 'HASH'
    
    # Validate billing mode
    assert 'BillingModeSummary' in table_description
    assert table_description['BillingModeSummary']['BillingMode'] == 'PAY_PER_REQUEST'
    
    # Check initial item count
    scan_response = dynamodb_client.scan(TableName=table_name)
    initial_count = scan_response['Count']
    
    assert initial_count == 0, f"New table should be empty, found {initial_count} items"
    
    print(f"Table '{table_name}' created successfully")
    print(f"Table status: {table_description['TableStatus']}, Item count: {initial_count}")


def test_create_item_operation(dynamodb_client, test_table, health_check):
    """
    Test DynamoDB PUT item operation.
    Validates item creation with proper attributes and capacity consumption.
    """
    table_name = test_table.table_name
    
    # Test item data
    test_item = {
        'Id': {'S': '123'},
        'name': {'S': 'Batman'}
    }
    
    # Create item with capacity tracking
    response = dynamodb_client.put_item(
        TableName=table_name,
        Item=test_item,
        ReturnConsumedCapacity='TOTAL',
        ReturnItemCollectionMetrics='SIZE'
    )
    
    # Validate response
    assert 'ConsumedCapacity' in response
    consumed_capacity = response['ConsumedCapacity']['CapacityUnits']
    assert consumed_capacity > 0, "PUT operation should consume capacity"
    
    # Verify item was created by retrieving it
    get_response = dynamodb_client.get_item(
        TableName=table_name,
        Key={'Id': {'S': '123'}}
    )
    
    assert 'Item' in get_response, "Created item should be retrievable"
    retrieved_item = get_response['Item']
    assert retrieved_item['Id']['S'] == '123'
    assert retrieved_item['name']['S'] == 'Batman'
    
    print(f"Item created successfully: {{'Id': '123', 'name': 'Batman'}}")
    print(f"Create operation consumed capacity: {consumed_capacity} units")


def test_read_operations_scan_and_get(dynamodb_client, test_table, health_check):
    """
    Test DynamoDB read operations: SCAN and GET.
    Validates item retrieval using different access patterns.
    """
    table_name = test_table.table_name
    
    # First, create test items
    test_items = [
        {'Id': {'S': '123'}, 'name': {'S': 'Batman'}},
        {'Id': {'S': '456'}, 'name': {'S': 'Superman'}},
        {'Id': {'S': '789'}, 'name': {'S': 'Wonder Woman'}}
    ]
    
    for item in test_items:
        dynamodb_client.put_item(TableName=table_name, Item=item)
    
    # Test SCAN operation
    scan_response = dynamodb_client.scan(TableName=table_name)
    
    assert scan_response['Count'] == len(test_items), f"Scan should return {len(test_items)} items"
    assert scan_response['ScannedCount'] == len(test_items), "Scanned count should match item count"
    
    # Validate scan results
    scanned_ids = {item['Id']['S'] for item in scan_response['Items']}
    expected_ids = {'123', '456', '789'}
    assert scanned_ids == expected_ids, "Scan should return all created items"
    
    # Test GET operation for specific item
    get_response = dynamodb_client.get_item(
        TableName=table_name,
        Key={'Id': {'S': '123'}}
    )
    
    assert 'Item' in get_response, "GET operation should return the requested item"
    retrieved_item = get_response['Item']
    assert retrieved_item['Id']['S'] == '123'
    assert retrieved_item['name']['S'] == 'Batman'
    
    # Test GET for non-existent item
    get_missing_response = dynamodb_client.get_item(
        TableName=table_name,
        Key={'Id': {'S': '999'}}
    )
    
    assert 'Item' not in get_missing_response, "GET for non-existent item should return empty"
    
    print(f"Scan operation found {scan_response['Count']} items")
    print(f"Get operation retrieved: {{'Id': '123', 'name': 'Batman'}}")
    print("Read operations completed successfully")


def test_update_item_operation(dynamodb_client, test_table, health_check):
    """
    Test DynamoDB UPDATE item operation.
    Validates item updates with SET expressions and attribute handling.
    """
    table_name = test_table.table_name
    
    # Create initial item
    initial_item = {
        'Id': {'S': '123'},
        'name': {'S': 'Batman'}
    }
    
    dynamodb_client.put_item(TableName=table_name, Item=initial_item)
    
    # Update item with new attributes
    update_response = dynamodb_client.update_item(
        TableName=table_name,
        Key={'Id': {'S': '123'}},
        UpdateExpression='SET #name = :n, age = :a',
        ExpressionAttributeNames={'#name': 'name'},
        ExpressionAttributeValues={
            ':n': {'S': 'Robin'},
            ':a': {'N': '35'}
        },
        ReturnValues='ALL_NEW',
        ReturnConsumedCapacity='TOTAL'
    )
    
    # Validate update response
    assert 'Attributes' in update_response, "Update should return updated attributes"
    updated_attributes = update_response['Attributes']
    
    assert updated_attributes['Id']['S'] == '123'
    assert updated_attributes['name']['S'] == 'Robin'
    assert updated_attributes['age']['N'] == '35'
    
    # Validate capacity consumption
    consumed_capacity = update_response['ConsumedCapacity']['CapacityUnits']
    assert consumed_capacity > 0, "Update operation should consume capacity"
    
    # Verify update by retrieving item
    get_response = dynamodb_client.get_item(
        TableName=table_name,
        Key={'Id': {'S': '123'}}
    )
    
    retrieved_item = get_response['Item']
    assert retrieved_item['name']['S'] == 'Robin', "Name should be updated to Robin"
    assert retrieved_item['age']['N'] == '35', "Age should be set to 35"
    
    print(f"Item updated successfully: {{'Id': '123', 'name': 'Robin', 'age': 35}}")
    print(f"Update operation consumed capacity: {consumed_capacity} units")


def test_delete_item_operation(dynamodb_client, test_table, health_check):
    """
    Test DynamoDB DELETE item operation.
    Validates item deletion and capacity consumption.
    """
    table_name = test_table.table_name
    
    # Create item to delete
    test_item = {
        'Id': {'S': '123'},
        'name': {'S': 'Batman'},
        'age': {'N': '35'}
    }
    
    dynamodb_client.put_item(TableName=table_name, Item=test_item)
    
    # Verify item exists before deletion
    get_response = dynamodb_client.get_item(
        TableName=table_name,
        Key={'Id': {'S': '123'}}
    )
    assert 'Item' in get_response, "Item should exist before deletion"
    
    # Delete item
    delete_response = dynamodb_client.delete_item(
        TableName=table_name,
        Key={'Id': {'S': '123'}},
        ReturnConsumedCapacity='TOTAL',
        ReturnValues='ALL_OLD'
    )
    
    # Validate delete response
    assert 'ConsumedCapacity' in delete_response
    consumed_capacity = delete_response['ConsumedCapacity']['CapacityUnits']
    assert consumed_capacity > 0, "Delete operation should consume capacity"
    
    # Validate returned attributes (before deletion)
    if 'Attributes' in delete_response:
        deleted_attributes = delete_response['Attributes']
        assert deleted_attributes['Id']['S'] == '123'
        assert deleted_attributes['name']['S'] == 'Batman'
    
    # Verify item no longer exists
    get_after_delete = dynamodb_client.get_item(
        TableName=table_name,
        Key={'Id': {'S': '123'}}
    )
    assert 'Item' not in get_after_delete, "Item should not exist after deletion"
    
    print("Item deleted successfully")
    print(f"Delete operation consumed capacity: {consumed_capacity} units")


def test_crud_full_workflow(dynamodb_client, test_table, health_check):
    """
    Test complete CRUD workflow in sequence.
    Validates the entire lifecycle from creation to cleanup.
    """
    table_name = test_table.table_name
    
    # Step 1: CREATE - Add multiple items
    test_items = [
        {'Id': {'S': '100'}, 'name': {'S': 'Clark Kent'}, 'role': {'S': 'Reporter'}},
        {'Id': {'S': '200'}, 'name': {'S': 'Bruce Wayne'}, 'role': {'S': 'CEO'}},
        {'Id': {'S': '300'}, 'name': {'S': 'Diana Prince'}, 'role': {'S': 'Ambassador'}}
    ]
    
    created_items = 0
    for item in test_items:
        response = dynamodb_client.put_item(TableName=table_name, Item=item)
        created_items += 1
    
    assert created_items == len(test_items), f"Should create {len(test_items)} items"
    
    # Step 2: READ - Verify all items exist
    scan_response = dynamodb_client.scan(TableName=table_name)
    assert scan_response['Count'] == len(test_items), "All items should be readable"
    
    # Step 3: UPDATE - Modify one item
    update_response = dynamodb_client.update_item(
        TableName=table_name,
        Key={'Id': {'S': '100'}},
        UpdateExpression='SET #role = :r, age = :a',
        ExpressionAttributeNames={'#role': 'role'},
        ExpressionAttributeValues={
            ':r': {'S': 'Superhero'},
            ':a': {'N': '30'}
        },
        ReturnValues='ALL_NEW'
    )
    
    updated_attributes = update_response['Attributes']
    assert updated_attributes['role']['S'] == 'Superhero', "Role should be updated"
    assert updated_attributes['age']['N'] == '30', "Age should be added"
    
    # Step 4: DELETE - Remove items
    deleted_items = 0
    for item in test_items:
        dynamodb_client.delete_item(
            TableName=table_name,
            Key={'Id': item['Id']}
        )
        deleted_items += 1
    
    # Step 5: VERIFY - Confirm cleanup
    final_scan = dynamodb_client.scan(TableName=table_name)
    assert final_scan['Count'] == 0, "Table should be empty after cleanup"
    
    print("Full CRUD workflow completed successfully")
    print(f"Created: {created_items}, Updated: 1, Deleted: {deleted_items}")
    print("Final verification: Table is empty after cleanup")


def test_concurrent_operations(dynamodb_client, test_table, health_check):
    """
    Test concurrent DynamoDB operations to validate thread safety.
    """
    table_name = test_table.table_name
    results = queue.Queue()
    num_threads = 10
    
    def perform_crud_operation(thread_id):
        """Helper function for concurrent CRUD operations"""
        try:
            start_time = time.time()
            
            # Create item
            item_id = f"thread-{thread_id}"
            create_response = dynamodb_client.put_item(
                TableName=table_name,
                Item={
                    'Id': {'S': item_id},
                    'name': {'S': f'User {thread_id}'},
                    'thread_id': {'N': str(thread_id)}
                }
            )
            
            # Read item
            get_response = dynamodb_client.get_item(
                TableName=table_name,
                Key={'Id': {'S': item_id}}
            )
            
            # Update item
            update_response = dynamodb_client.update_item(
                TableName=table_name,
                Key={'Id': {'S': item_id}},
                UpdateExpression='SET #name = :n',
                ExpressionAttributeNames={'#name': 'name'},
                ExpressionAttributeValues={':n': {'S': f'Updated User {thread_id}'}},
                ReturnValues='ALL_NEW'
            )
            
            # Delete item
            delete_response = dynamodb_client.delete_item(
                TableName=table_name,
                Key={'Id': {'S': item_id}}
            )
            
            end_time = time.time()
            operation_time = int((end_time - start_time) * 1000)
            
            results.put({
                'thread_id': thread_id,
                'success': True,
                'operation_time': operation_time,
                'created': 'Item' in get_response,
                'updated': 'Attributes' in update_response
            })
            
        except Exception as e:
            results.put({
                'thread_id': thread_id,
                'success': False,
                'error': str(e),
                'operation_time': 0
            })
    
    # Start concurrent threads
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=perform_crud_operation, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join(timeout=30)
    
    # Analyze results
    successful_operations = 0
    total_operation_time = 0
    
    while not results.empty():
        result = results.get()
        if result['success']:
            successful_operations += 1
            total_operation_time += result['operation_time']
        else:
            print(f"Thread {result['thread_id']} failed: {result.get('error', 'Unknown error')}")
    
    success_rate = successful_operations / num_threads * 100
    avg_operation_time = total_operation_time / successful_operations if successful_operations > 0 else 0
    
    # Validate concurrent performance
    assert success_rate >= 90, f"Concurrent operation success rate too low: {success_rate}%"
    assert successful_operations >= num_threads - 2, f"Too many failed concurrent operations"
    
    # Verify table is clean after concurrent operations
    final_scan = dynamodb_client.scan(TableName=table_name)
    remaining_items = final_scan['Count']
    assert remaining_items == 0, f"Table should be clean after concurrent operations, found {remaining_items} items"
    
    print("Concurrent operations test passed")
    print(f"Results: Success_Rate={success_rate}%, Avg_Operation_Time={int(avg_operation_time)}ms, Successful_Operations={successful_operations}/{num_threads}")


def test_performance_and_capacity(dynamodb_client, test_table, health_check):
    """
    Test DynamoDB performance metrics and capacity consumption tracking.
    """
    table_name = test_table.table_name
    
    # Perform multiple operations to measure performance
    num_operations = 20
    operation_times = []
    total_consumed_capacity = 0
    
    for i in range(num_operations):
        start_time = time.time()
        
        # Create item
        create_response = dynamodb_client.put_item(
            TableName=table_name,
            Item={
                'Id': {'S': f'perf-test-{i}'},
                'name': {'S': f'Performance Test Item {i}'},
                'index': {'N': str(i)},
                'timestamp': {'S': datetime.now().isoformat()}
            },
            ReturnConsumedCapacity='TOTAL'
        )
        
        end_time = time.time()
        operation_time = int((end_time - start_time) * 1000)
        operation_times.append(operation_time)
        
        # Track capacity consumption
        if 'ConsumedCapacity' in create_response:
            total_consumed_capacity += create_response['ConsumedCapacity']['CapacityUnits']
    
    # Analyze performance metrics
    avg_operation_time = sum(operation_times) / len(operation_times)
    min_operation_time = min(operation_times)
    max_operation_time = max(operation_times)
    
    # Performance assertions
    assert avg_operation_time < 100, f"Average operation time too slow: {avg_operation_time}ms"
    assert min_operation_time < 50, f"Minimum operation time too slow: {min_operation_time}ms"
    assert total_consumed_capacity > 0, "Operations should consume capacity"
    
    # Verify all items were created
    scan_response = dynamodb_client.scan(TableName=table_name)
    assert scan_response['Count'] == num_operations, f"Should have {num_operations} items"
    
    # Test batch operations for comparison
    batch_start = time.time()
    
    # Clean up items for batch delete test
    with test_table.batch_writer() as batch:
        for i in range(num_operations):
            batch.delete_item(Key={'Id': f'perf-test-{i}'})
    
    batch_end = time.time()
    batch_time = int((batch_end - batch_start) * 1000)
    
    # Verify cleanup
    final_scan = dynamodb_client.scan(TableName=table_name)
    assert final_scan['Count'] == 0, "Table should be empty after batch cleanup"
    
    print(f"Performance test completed: avg={int(avg_operation_time)}ms, operations={num_operations}, total_capacity={total_consumed_capacity} units")
    print(f"Batch operation time: {batch_time}ms for {num_operations} deletes")


def test_error_handling_and_edge_cases(dynamodb_client, test_table, health_check):
    """
    Test error handling scenarios and edge cases.
    """
    table_name = test_table.table_name
    
    # Test 1: Conditional PUT that should fail
    # First create an item
    dynamodb_client.put_item(
        TableName=table_name,
        Item={'Id': {'S': 'conditional-test'}, 'name': {'S': 'Original'}}
    )
    
    # Try to create same item with condition that it doesn't exist
    with pytest.raises(ClientError) as exc_info:
        dynamodb_client.put_item(
            TableName=table_name,
            Item={'Id': {'S': 'conditional-test'}, 'name': {'S': 'Duplicate'}},
            ConditionExpression='attribute_not_exists(Id)'
        )
    
    assert exc_info.value.response['Error']['Code'] == 'ConditionalCheckFailedException'
    
    # Test 2: Update non-existent item with condition
    with pytest.raises(ClientError) as exc_info:
        dynamodb_client.update_item(
            TableName=table_name,
            Key={'Id': {'S': 'non-existent'}},
            UpdateExpression='SET #name = :n',
            ConditionExpression='attribute_exists(Id)',
            ExpressionAttributeNames={'#name': 'name'},
            ExpressionAttributeValues={':n': {'S': 'Should Fail'}}
        )
    
    assert exc_info.value.response['Error']['Code'] == 'ConditionalCheckFailedException'
    
    # Test 3: Invalid table name
    with pytest.raises(ClientError) as exc_info:
        dynamodb_client.get_item(
            TableName='NonExistentTable',
            Key={'Id': {'S': 'test'}}
        )
    
    assert exc_info.value.response['Error']['Code'] == 'ResourceNotFoundException'
    
    # Test 4: Malformed key
    with pytest.raises(ClientError) as exc_info:
        dynamodb_client.get_item(
            TableName=table_name,
            Key={'WrongKey': {'S': 'test'}}
        )
    
    assert exc_info.value.response['Error']['Code'] == 'ValidationException'
    
    print("Error handling test passed - all expected errors were properly raised")


def test_data_types_and_attributes(dynamodb_client, test_table, health_check):
    """
    Test various DynamoDB data types and attribute handling.
    """
    table_name = test_table.table_name
    
    # Create item with various data types
    complex_item = {
        'Id': {'S': 'data-types-test'},
        'string_attr': {'S': 'Hello World'},
        'number_attr': {'N': '42'},
        'binary_attr': {'B': b'binary data'},
        'boolean_attr': {'BOOL': True},
        'null_attr': {'NULL': True},
        'list_attr': {'L': [
            {'S': 'item1'},
            {'N': '123'},
            {'BOOL': False}
        ]},
        'map_attr': {'M': {
            'nested_string': {'S': 'nested value'},
            'nested_number': {'N': '99'}
        }},
        'string_set': {'SS': ['value1', 'value2', 'value3']},
        'number_set': {'NS': ['1', '2', '3']},
        'decimal_attr': {'N': '123.456'}
    }
    
    # Put item with all data types
    put_response = dynamodb_client.put_item(
        TableName=table_name,
        Item=complex_item,
        ReturnConsumedCapacity='TOTAL'
    )
    
    assert 'ConsumedCapacity' in put_response
    
    # Retrieve and validate item
    get_response = dynamodb_client.get_item(
        TableName=table_name,
        Key={'Id': {'S': 'data-types-test'}}
    )
    
    assert 'Item' in get_response
    retrieved_item = get_response['Item']
    
    # Validate each data type
    assert retrieved_item['string_attr']['S'] == 'Hello World'
    assert retrieved_item['number_attr']['N'] == '42'
    assert retrieved_item['boolean_attr']['BOOL'] == True
    assert retrieved_item['null_attr']['NULL'] == True
    assert len(retrieved_item['list_attr']['L']) == 3
    assert 'nested_string' in retrieved_item['map_attr']['M']
    assert len(retrieved_item['string_set']['SS']) == 3
    assert len(retrieved_item['number_set']['NS']) == 3
    
    # Test attribute updates
    update_response = dynamodb_client.update_item(
        TableName=table_name,
        Key={'Id': {'S': 'data-types-test'}},
        UpdateExpression='SET string_attr = :s ADD number_attr :inc',
        ExpressionAttributeValues={
            ':s': {'S': 'Updated String'},
            ':inc': {'N': '10'}
        },
        ReturnValues='ALL_NEW'
    )
    
    updated_item = update_response['Attributes']
    assert updated_item['string_attr']['S'] == 'Updated String'
    assert updated_item['number_attr']['N'] == '52'  # 42 + 10
    
    print("Data types and attributes test passed - all DynamoDB data types handled correctly")