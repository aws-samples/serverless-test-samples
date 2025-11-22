# End-to-End Tests

This directory contains end-to-end tests that validate complete user workflows through the real API Gateway endpoint.

## Overview

E2E tests validate the entire system working together:
- **API Gateway** with IAM authorization
- **Lambda functions** (cold/warm starts)
- **DynamoDB** persistence
- **EventBridge** event delivery
- **Async processing** (notification Lambda)
- **Business rules** (circular dependencies, status transitions)

## Prerequisites

### 1. Deploy Infrastructure

E2E tests require both main application and test harness to be deployed:

```bash
# Deploy main application
make deploy

# Deploy test harness (optional, for event verification)
make deploy-test-infra
```

### 2. AWS Credentials

E2E tests use your AWS credentials to sign requests with SigV4:

```bash
# Ensure credentials are configured
aws configure

# Or use environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-west-2
```

### 3. Get API Endpoint

The tests automatically retrieve the API endpoint from CloudFormation stack outputs. Alternatively, set it manually:

```bash
export API_ENDPOINT="https://your-api-id.execute-api.us-west-2.amazonaws.com/prod"
```

## Running E2E Tests

### All E2E Tests

```bash
# Using Make
make test-e2e

# Or using pytest directly
poetry run pytest tests/e2e -v -m e2e

# Or using test script
poetry run test-e2e
```

### Specific Test

```bash
# Run specific test file
poetry run pytest tests/e2e/test_task_lifecycle_e2e.py -v

# Run specific test method
poetry run pytest tests/e2e/test_task_lifecycle_e2e.py::TestTaskLifecycleE2E::test_complete_task_lifecycle_with_dependencies -v
```

### With Verbose Output

```bash
# See detailed test output
poetry run pytest tests/e2e -v -s
```

## Test Scenarios

### 1. Complete Task Lifecycle with Dependencies

**Test**: `test_complete_task_lifecycle_with_dependencies`

**Flow**:
1. Create parent task via API Gateway
2. Verify parent task in DynamoDB
3. Create child task with dependency on parent
4. Verify child task with correct dependencies
5. Wait for async EventBridge processing
6. Verify events were published
7. Update parent task status
8. Verify update propagated
9. Retrieve tasks via API
10. Cleanup test data

**Validates**:
- API Gateway IAM authorization (SigV4 signing)
- Lambda invocation through API Gateway
- DynamoDB CRUD operations
- EventBridge event publishing
- Async notification processing
- Dependency management
- Status updates
- Error handling

### 2. Circular Dependency Prevention

**Test**: `test_circular_dependency_prevention_e2e`

**Flow**:
1. Create task A
2. Create task B with dependency on A
3. Try to update A to depend on B (should fail)
4. Verify error response
5. Cleanup

**Validates**:
- Business rule enforcement (circular dependencies)
- Error handling across API → Lambda → Domain
- Proper HTTP error codes
- Error message formatting

## IAM Authorization

The API Gateway uses IAM authorization, which means:

1. **Requests must be signed** with AWS SigV4
2. **Credentials required**: AWS access key and secret key
3. **Permissions needed**: `execute-api:Invoke` on the API

### How Signing Works

The tests use `botocore.auth.SigV4Auth` to sign requests:

```python
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

# Create request
request = AWSRequest(
    method='POST',
    url='https://api-id.execute-api.region.amazonaws.com/prod/tasks',
    data=json.dumps({'title': 'My Task'}),
    headers={'Content-Type': 'application/json'}
)

# Sign with your credentials
credentials = boto3.Session().get_credentials()
SigV4Auth(credentials, 'execute-api', 'us-west-2').add_auth(request)

# Make request with signed headers
response = requests.post(url, headers=dict(request.headers), json=body)
```

### Required IAM Permissions

Your AWS credentials need these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "execute-api:Invoke",
      "Resource": "arn:aws:execute-api:region:account:api-id/*"
    }
  ]
}
```

## Test Data Management

### Automatic Cleanup

All E2E tests include cleanup in `finally` blocks to ensure test data is removed even if tests fail.

### Manual Cleanup

If tests fail and leave data:

```bash
# List tasks in DynamoDB
aws dynamodb scan --table-name cns427-task-api-tasks --select COUNT

# Delete specific task
aws dynamodb delete-item \
  --table-name cns427-task-api-tasks \
  --key '{"task_id":{"S":"your-task-id"}}'
```

## Troubleshooting

### Issue: API Endpoint Not Found

**Error**: `Could not get API endpoint`

**Solution**:
```bash
# Set manually
export API_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name cns427-task-api-api \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text)

# Or check CloudFormation console for the output
```

### Issue: 403 Forbidden

**Error**: `403 Forbidden` when calling API

**Solution**:
- Check AWS credentials are configured: `aws sts get-caller-identity`
- Verify IAM permissions for `execute-api:Invoke`
- Ensure API Gateway has IAM authorization enabled

### Issue: Signature Mismatch

**Error**: `SignatureDoesNotMatch`

**Solution**:
- Check system clock is synchronized
- Verify AWS region matches API region
- Ensure credentials are valid

### Issue: 502 Bad Gateway

**Error**: `502 Bad Gateway` or `Internal server error`

**Solution**:
1. **Check Lambda logs** (most common cause):
   ```bash
   aws logs tail /aws/lambda/cns427-task-api-task-handler --follow --region us-west-2
   ```

2. **Wait after deployment**: Lambda may need time to initialize
   ```bash
   # After deploying, wait 30-60 seconds before running E2E tests
   make deploy
   sleep 60
   make test-e2e
   ```

3. **Verify environment variables**:
   ```bash
   aws lambda get-function-configuration \
     --function-name cns427-task-api-task-handler \
     --query 'Environment.Variables'
   ```

4. **Check IAM permissions**: Lambda needs DynamoDB and EventBridge permissions

5. **Verify API Gateway integration**:
   ```bash
   aws apigateway get-rest-apis --query 'items[?name==`cns427-task-api-api`]'
   ```

### Issue: Tasks Not Found in DynamoDB

**Error**: Task not found after creation

**Solution**:
- Increase wait time for eventual consistency
- Check DynamoDB table name is correct
- Verify Lambda has permissions to write to DynamoDB

### Issue: Events Not Captured in Test Harness

**This is expected behavior for E2E tests!**

E2E tests use **real events** (source: `cns427-task-api`, detailType: `TaskCreated`), which are NOT captured by the test harness.

The test harness only captures **TEST-* events** (source: `TEST-cns427-task-api`, detailType: `TEST-TaskCreated`) used by integration tests.

**Why?**
- **E2E tests**: Verify production flow with real events
- **Integration tests**: Use TEST- prefix for isolated testing
- **Test harness**: Only captures TEST- events to avoid mixing test and production data

**To verify EventBridge in E2E tests**:
- Check CloudWatch metrics for notification Lambda invocations
- Check CloudWatch logs for notification Lambda
- Verify the full workflow completes successfully (which proves events were delivered)

## Performance

E2E tests are slower than unit/integration tests:

- **Unit tests**: < 1 second (in-memory)
- **Integration tests**: 1-5 seconds (real AWS, single service)
- **E2E tests**: 5-15 seconds (full workflow, multiple services, async processing)

This is expected and acceptable for E2E tests.

## Best Practices

1. **Run E2E tests less frequently**: Before commits, not on every save
2. **Use descriptive test run IDs**: Makes debugging easier
3. **Always cleanup**: Use `finally` blocks
4. **Wait for async operations**: EventBridge processing takes time
5. **Check CloudWatch logs**: If tests fail, check Lambda logs
6. **Isolate test data**: Use unique IDs to avoid conflicts

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on:
  push:
    branches: [main]
  pull_request:

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-west-2
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: poetry install
      
      - name: Run E2E tests
        run: make test-e2e
```

## Next Steps

- **[Testing Guide](../../docs/testing-guide.md)** - Overall testing strategy
- **[Deployment Guide](../../docs/deployment.md)** - Deploy infrastructure
- **[Architecture Guide](../../docs/architecture.md)** - Understand the architecture
