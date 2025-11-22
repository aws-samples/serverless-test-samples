# Integration Tests

This directory contains integration tests that test the full Task API flow using real AWS services.

## Test Strategy

### DynamoDB Integration Tests (`test_dynamodb_integration.py`)
- **Purpose**: Test complete CRUD flow through API Gateway → Lambda → DynamoDB
- **AWS Services**: Uses real DynamoDB table for data persistence, fake EventBridge for event capture
- **EventBridge**: Stubbed to capture events without publishing
- **Verification**: Direct DynamoDB queries to verify data persistence

### Error Simulation Tests (`test_task_api_error_simulation.py`)
- **Purpose**: Test error handling scenarios without affecting real AWS resources
- **DynamoDB**: Uses error-simulating fake repository
- **EventBridge**: Stubbed to capture events
- **Error Types**: Throttling, access denied, resource not found, validation errors, service unavailable

## Prerequisites

### AWS Credentials
Integration tests require AWS credentials configured:
```bash
aws configure
# OR
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=us-east-1
```

### DynamoDB Table
Tests require a DynamoDB table for testing. Set the table name:
```bash
export TEST_TASKS_TABLE_NAME=cns427-task-api-test
```

**Table Schema:**
- **Table Name**: `cns427-task-api-test` (or your custom name)
- **Partition Key**: `task_id` (String)
- **Billing Mode**: Pay-per-request (recommended for testing)

### IAM Permissions
The AWS credentials need the following DynamoDB permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Scan"
            ],
            "Resource": "arn:aws:dynamodb:*:*:table/cns427-task-api-test"
        }
    ]
}
```

## Running Tests

### All Integration Tests
```bash
make test-integration
# OR
./scripts/run-tests.sh --type integration
# OR
poetry run pytest tests/integration -m integration
```

### Specific Test Files
```bash
# DynamoDB integration tests
poetry run pytest tests/integration/test_dynamodb_integration.py -v

# Error simulation tests
poetry run pytest tests/integration/test_task_api_error_simulation.py -v
```

### With Custom Table Name
```bash
TEST_TASKS_TABLE_NAME=my-test-table poetry run pytest tests/integration -m integration
```

## Test Data Management

### Automatic Cleanup
- Each test cleans up its own test data
- Uses `try/finally` blocks to ensure cleanup even if tests fail
- Helper functions: `cleanup_task_from_dynamodb(task_id)`

### Manual Cleanup
If tests fail and leave test data:
```bash
# List items in test table
aws dynamodb scan --table-name cns427-task-api-test --select COUNT

# Delete specific item
aws dynamodb delete-item --table-name cns427-task-api-test --key '{"task_id":{"S":"your-task-id"}}'
```

## Test Structure

### Happy Path Tests
- `test_create_task_end_to_end`: Complete task creation flow
- `test_get_task_end_to_end`: Task retrieval with DynamoDB verification
- `test_update_task_end_to_end`: Task update with version control
- `test_delete_task_end_to_end`: Task deletion with cleanup verification
- `test_list_tasks_end_to_end`: Task listing with pagination

### Error Handling Tests
- `test_get_nonexistent_task_returns_404`: 404 error handling
- `test_create_task_validation_error_returns_400`: Input validation

### Error Simulation Tests
- `test_create_task_throttling_error_returns_500`: DynamoDB throttling
- `test_create_task_access_denied_error_returns_500`: Permission errors
- `test_get_task_resource_not_found_error_returns_500`: Resource errors
- `test_update_task_validation_error_returns_500`: Validation errors
- `test_list_tasks_service_unavailable_error_returns_500`: Service errors

## Benefits

### Real AWS Integration
- ✅ Tests actual AWS SDK behavior
- ✅ Validates real DynamoDB operations
- ✅ Tests actual data persistence and retrieval
- ✅ No LocalStack complexity or version mismatches

### Error Simulation
- ✅ Predictable error conditions
- ✅ Fast execution (no network calls for errors)
- ✅ Comprehensive error scenario coverage
- ✅ No risk to real AWS resources

### EventBridge Stubbing
- ✅ Captures events for verification
- ✅ No unintended side effects
- ✅ Tests event content and timing
- ✅ Fast and reliable

## Troubleshooting

### Common Issues

**AWS Credentials Not Found**
```
Error: AWS credentials not configured
Solution: Run 'aws configure' or set environment variables
```

**DynamoDB Table Not Found**
```
Error: ResourceNotFoundException
Solution: Create the test table or check TEST_TASKS_TABLE_NAME
```

**Permission Denied**
```
Error: AccessDeniedException
Solution: Check IAM permissions for DynamoDB operations
```

### Debug Mode
Run tests with verbose output:
```bash
poetry run pytest tests/integration -v -s
```

### Test Isolation
Each test is isolated and cleans up its own data. If you need to inspect test data, add a breakpoint or sleep before cleanup:
```python
# In test code
import time
time.sleep(30)  # Inspect DynamoDB table manually
```