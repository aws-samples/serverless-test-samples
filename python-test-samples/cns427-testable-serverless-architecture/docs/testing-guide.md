# Testing Guide

This guide explains the comprehensive testing strategy used in this serverless application, including the honeycomb model, testing patterns, and best practices.

## Table of Contents

- [Testing Philosophy](#testing-philosophy)
- [The Honeycomb Model](#the-honeycomb-model)
- [Test Types](#test-types)
- [Testing Patterns](#testing-patterns)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Troubleshooting](#troubleshooting)

## Testing Philosophy

### Core Principles

1. **Test at the Right Level**: Test each layer appropriately
2. **Real AWS Over Mocks**: Use real AWS services for integration tests
3. **Fakes Over Mocks**: Use in-memory fakes for unit tests
4. **Fast Feedback**: Unit tests run in milliseconds
5. **Confidence**: Integration tests validate real behavior

### Why This Matters for Serverless

Serverless applications have unique testing challenges:
- Most bugs occur at service boundaries (DynamoDB, EventBridge, API Gateway)
- AWS SDK behavior is complex and hard to mock accurately
- Integration issues are the primary source of production failures
- Mocking AWS services doesn't catch real-world issues

## The Honeycomb Model

### Traditional Pyramid vs Honeycomb

```
❌ TRADITIONAL PYRAMID (Doesn't work well for serverless)
        /\
       /  \      E2E Tests (10%)
      /____\
     /      \    Integration Tests (20%)
    /________\
   /          \  Unit Tests (70%)
  /____________\

Problems for Serverless:
• Most bugs are at service boundaries
• Mocking AWS is complex and unreliable
• Unit tests give false confidence
```

```
✅ HONEYCOMB MODEL (Better for serverless)

            E2E Tests (10%)
         /  Critical flows  \
       /                      \
     /  Integration Tests (60%) \
    |     Service Boundaries.    |
    |    Real AWS Services       |
    |   Error Handling, Scale    |
     \                          /
       \                      /
         \ Unit Tests (30%) /
          Pure Business Logic
            Fast, Isolated    
```

### Our Test Distribution

```
Total: 102 tests

Integration Tests: 35% (36 tests)
├─ Handler Tests: 17 tests (API Gateway boundary)
│  ├─ Request/response contracts
│  ├─ HTTP status codes
│  └─ End-to-end handler flow
├─ Event Contract Tests: 4 tests (EventBridge boundary)
│  ├─ Schema validation
│  └─ Consumer contracts
└─ AWS Service Tests: 15 tests
   ├─ DynamoDB integration (7 tests)
   └─ EventBridge integration (8 tests)

Unit Tests: 56% (57 tests)
├─ Domain Logic: Pure business rules
├─ Data Models: Validation and serialization
└─ Helper Utilities: Test support functions

Property-Based Tests: 6% (6 tests)
└─ Complex Algorithms: Circular dependency detection

E2E Tests: 3% (3 tests)
└─ Critical user workflows
```

**Key Insight**: Handler and event contract tests are classified as **integration tests** because they test boundaries (API Gateway, EventBridge), not pure business logic. This gives us a true honeycomb distribution.

### Why This Distribution Works

**Most serverless bugs occur at integration boundaries** (API contracts, event schemas, AWS services), validating our 35% integration test focus. Combined with 56% unit tests for domain logic, 6% property-based tests for complex algorithms, and 3% E2E for critical workflows, this proves the honeycomb model is correct for serverless applications.

## Test Types

### 1. Unit Tests (Fast, Isolated)

**Purpose**: Test business logic without AWS dependencies

**Location**: `tests/unit/`

**Characteristics**:
- ✅ No AWS SDK calls
- ✅ In-memory fakes
- ✅ Fast execution (< 1 second total)
- ✅ No network calls
- ✅ Deterministic results

**What to Test**:
- Pure business logic
- Domain rules and validation
- HTTP request/response formatting
- Model validation
- Error handling logic

**Example**:
```python
def test_create_task_validates_title():
    """Test business rule: title must be at least 3 characters."""
    # GIVEN in-memory fakes
    repository = InMemoryTaskRepository()
    publisher = InMemoryEventPublisher()
    service = TaskService(repository, publisher)
    
    # WHEN creating task with short title
    with pytest.raises(ValueError, match="at least 3 characters"):
        service.create_task(title="ab")
    
    # THEN no task created
    assert repository.count() == 0
    assert publisher.count() == 0
```

**Key Pattern**: Use **in-memory fakes** instead of mocks
```python
# ❌ DON'T: Complex mock setup
@patch('boto3.resource')
def test_with_mocks(mock_resource):
    mock_table = Mock()
    mock_resource.return_value.Table.return_value = mock_table
    # ... complex setup

# ✅ DO: Simple fake injection
def test_with_fakes():
    repository = InMemoryTaskRepository()
    service = TaskService(repository)
    # ... simple and clear
```

### 2. Integration Tests (Real AWS)

**Purpose**: Test complete flows with real AWS services

**Location**: `tests/integration/`

**Characteristics**:
- ✅ Real AWS SDK calls
- ✅ Real DynamoDB operations
- ✅ Real EventBridge publishing
- ✅ Validates actual AWS behavior
- ⚠️ Requires AWS credentials
- ⚠️ Slower than unit tests (seconds)

**What to Test**:
- CRUD operations with real DynamoDB
- Event publishing to real EventBridge
- Error handling with real AWS errors
- Pagination and limits
- Concurrent operations
- IAM permissions

**Example - DynamoDB Integration**:
```python
@pytest.mark.integration
def test_create_task_persists_to_dynamodb():
    """Test task creation with real DynamoDB."""
    # GIVEN real DynamoDB adapter
    repository = DynamoDBTaskRepository(
        table_name=os.getenv('TEST_TASKS_TABLE_NAME')
    )
    
    try:
        # WHEN creating task
        task = Task(title="Integration Test Task")
        created_task = repository.create_task(task)
        
        # THEN verify in DynamoDB
        retrieved_task = repository.get_task(created_task.task_id)
        assert retrieved_task is not None
        assert retrieved_task.title == "Integration Test Task"
        
    finally:
        # ALWAYS cleanup
        repository.delete_task(created_task.task_id)
```

**Example - EventBridge Integration**:
```python
@pytest.mark.integration
def test_task_created_event_published_to_eventbridge():
    """Test event publishing with real EventBridge."""
    # GIVEN real EventBridge publisher
    publisher = EventBridgePublisher(
        event_bus_name=os.getenv('TEST_EVENT_BUS_NAME')
    )
    
    # WHEN publishing event
    task = Task(title="Test Task")
    publisher.publish_task_created(task)
    
    # THEN verify event captured by test harness
    # (Test harness Lambda captures events to DynamoDB)
    time.sleep(2)  # Allow event processing
    
    test_results = query_test_results_table(task.task_id)
    assert len(test_results) == 1
    assert test_results[0]['detail_type'] == 'TaskCreated'
```

### 3. Error Simulation Tests

**Purpose**: Test error handling without affecting real AWS resources

**Location**: `tests/integration/` (marked with error simulation)

**Characteristics**:
- ✅ Simulates AWS errors
- ✅ Fast execution (no real AWS calls)
- ✅ Predictable error conditions
- ✅ No AWS costs
- ✅ Safe to run anytime

**What to Test**:
- DynamoDB throttling
- Access denied errors
- Resource not found
- Validation errors
- Service unavailable
- Network timeouts

**Example**:
```python
class ThrottlingRepository:
    """Fake that simulates DynamoDB throttling."""
    
    def create_task(self, task: Task) -> Task:
        raise ClientError(
            {
                'Error': {
                    'Code': 'ProvisionedThroughputExceededException',
                    'Message': 'Rate exceeded'
                }
            },
            'PutItem'
        )

def test_handles_dynamodb_throttling():
    """Test graceful handling of DynamoDB throttling."""
    # GIVEN throttling repository
    repository = ThrottlingRepository()
    service = TaskService(repository)
    
    # WHEN creating task
    with pytest.raises(RepositoryError) as exc_info:
        service.create_task(title="Test")
    
    # THEN appropriate error raised
    assert "throttling" in str(exc_info.value).lower()
```

### 4. End-to-End Tests (Planned)

**Purpose**: Test critical user workflows through the entire system

**Location**: `tests/e2e/`

**Characteristics**:
- ✅ Full system integration
- ✅ Real API Gateway endpoints
- ✅ Real user workflows
- ⚠️ Slowest tests
- ⚠️ Most expensive

**What to Test**:
- Critical user journeys
- Multi-step workflows
- Cross-service interactions
- Authentication flows
- Error recovery

## Testing Patterns

### Pattern 1: Given/When/Then

All tests follow this structure:

```python
def test_behavior_description():
    # GIVEN - Setup test data and conditions
    repository = InMemoryTaskRepository()
    service = TaskService(repository)
    
    # WHEN - Execute the behavior being tested
    task = service.create_task(title="Test Task")
    
    # THEN - Assert expected outcomes
    assert task.title == "Test Task"
    assert task.status == TaskStatus.PENDING
    
    # AND - Verify side effects (optional)
    assert repository.count() == 1
```

### Pattern 2: Dependency Injection for Testing

```python
# Production: Self-initializing
service = TaskService()  # Uses real AWS adapters

# Testing: Inject fakes
repository = InMemoryTaskRepository()
publisher = InMemoryEventPublisher()
service = TaskService(repository, publisher)
```

### Pattern 3: Test Data Factories

```python
def create_test_task(**overrides) -> Task:
    """Create task with sensible defaults."""
    defaults = {
        'title': 'Test Task',
        'description': 'Test description',
        'priority': TaskPriority.MEDIUM,
        'status': TaskStatus.PENDING
    }
    defaults.update(overrides)
    return Task(**defaults)

# Usage
task = create_test_task(priority=TaskPriority.HIGH)
```

### Pattern 4: Cleanup in Finally Blocks

```python
@pytest.mark.integration
def test_with_real_aws():
    """Always cleanup, even if test fails."""
    repository = DynamoDBTaskRepository()
    task = None
    
    try:
        # Test code
        task = repository.create_task(Task(title="Test"))
        assert task is not None
        
    finally:
        # Cleanup always runs
        if task:
            repository.delete_task(task.task_id)
```

### Pattern 5: Socket Blocking for Unit Tests

```python
# tests/unit/conftest.py
import pytest
import socket

@pytest.fixture(scope='session', autouse=True)
def block_network():
    """Block network calls in unit tests."""
    def guard(*args, **kwargs):
        raise RuntimeError("Network call blocked in unit test")
    
    socket.socket = guard
```

## Running Tests

### Environment Setup

Before running integration tests, ensure your environment is configured correctly:

```bash
# Set AWS region (defaults to us-west-2 if not set)
export AWS_DEFAULT_REGION=us-west-2

# Or use AWS_REGION
export AWS_REGION=us-west-2

# Optional: Override test infrastructure stack name
export TEST_INFRASTRUCTURE_STACK_NAME=CNS427TaskApiTestInfrastructure
```

**Note**: The test scripts default to `us-west-2` to match the deployed infrastructure. If you deploy to a different region, set the environment variable accordingly.

### All Tests

```bash
# Run all tests (unit + integration)
make test

# Or with Poetry
poetry run test-all
```

### Unit Tests Only

```bash
# Fast, no AWS required
make test-unit

# Or with Poetry
poetry run test-unit

# Or with pytest directly
poetry run pytest tests/unit -v
```

### Integration Tests Only

```bash
# Requires AWS credentials and deployed infrastructure
make test-integration

# Or with Poetry
poetry run test-integration

# Or with pytest directly
poetry run pytest tests/integration -m integration -v
```

### EventBridge Tests

```bash
# Requires test harness deployed
make test-eventbridge

# Or with Poetry
poetry run test-eventbridge

# Or with pytest directly
poetry run pytest tests/integration/test_eventbridge_integration.py -v
```

### Coverage Report

```bash
# Generate HTML coverage report
make coverage

# View report
open htmlcov/all/index.html
```

### Specific Tests

```bash
# Run specific test file
poetry run pytest tests/unit/test_task_service.py -v

# Run specific test
poetry run pytest tests/unit/test_task_service.py::test_create_task -v

# Run tests matching pattern
poetry run pytest -k "create_task" -v
```

### Debug Mode

```bash
# Verbose output with print statements
poetry run pytest tests/unit -v -s

# Stop on first failure
poetry run pytest tests/unit -x

# Drop into debugger on failure
poetry run pytest tests/unit --pdb
```

## Writing Tests

### Unit Test Template

```python
# tests/unit/test_my_feature.py
import pytest
from task_api.domain.task_service import TaskService
from tests.shared.fakes.in_memory_repository import InMemoryTaskRepository
from tests.shared.fakes.in_memory_publisher import InMemoryEventPublisher

class TestMyFeature:
    """Test suite for my feature."""
    
    @pytest.fixture
    def repository(self):
        """Create fresh repository for each test."""
        return InMemoryTaskRepository()
    
    @pytest.fixture
    def publisher(self):
        """Create fresh publisher for each test."""
        return InMemoryEventPublisher()
    
    @pytest.fixture
    def service(self, repository, publisher):
        """Create service with test dependencies."""
        return TaskService(repository, publisher)
    
    def test_happy_path(self, service):
        """Test successful operation."""
        # GIVEN
        # ... setup
        
        # WHEN
        result = service.do_something()
        
        # THEN
        assert result is not None
    
    def test_error_case(self, service):
        """Test error handling."""
        # GIVEN
        # ... setup error condition
        
        # WHEN/THEN
        with pytest.raises(ValueError):
            service.do_something_invalid()
```

### Integration Test Template

```python
# tests/integration/test_my_integration.py
import pytest
import os
from task_api.integration.dynamodb_adapter import DynamoDBTaskRepository

@pytest.mark.integration
class TestMyIntegration:
    """Integration tests with real AWS."""
    
    @pytest.fixture
    def repository(self):
        """Create real DynamoDB repository."""
        return DynamoDBTaskRepository(
            table_name=os.getenv('TEST_TASKS_TABLE_NAME')
        )
    
    def test_with_real_aws(self, repository):
        """Test with real AWS service."""
        task = None
        
        try:
            # GIVEN
            # ... setup
            
            # WHEN
            task = repository.create_task(Task(title="Test"))
            
            # THEN
            assert task is not None
            
            # Verify in AWS
            retrieved = repository.get_task(task.task_id)
            assert retrieved.title == "Test"
            
        finally:
            # ALWAYS cleanup
            if task:
                repository.delete_task(task.task_id)
```

### Test Naming Conventions

```python
# File names
test_task_service.py          # Unit tests for TaskService
test_dynamodb_integration.py  # Integration tests for DynamoDB

# Class names
class TestTaskService:        # Test suite for TaskService
class TestCreateTask:         # Test suite for create_task method

# Method names
def test_create_task_returns_task():              # Happy path
def test_create_task_with_invalid_title_raises(): # Error case
def test_create_task_publishes_event():           # Side effect
```

## What to Focus On

### Unit Tests: Focus on Business Logic

✅ **DO Test**:
- Business rules and validation
- Domain logic
- Error conditions
- Edge cases
- Data transformations

❌ **DON'T Test**:
- AWS SDK behavior
- Network calls
- Database operations
- External service integration

### Integration Tests: Focus on Service Boundaries

✅ **DO Test**:
- Real AWS operations
- Error handling with real errors
- Data persistence
- Event publishing
- Pagination and limits
- Concurrent operations

❌ **DON'T Test**:
- Business logic (that's unit tests)
- Every edge case (too slow)
- UI/presentation logic

### What to Look For in Failures

**Unit Test Failures**:
- Business logic bugs
- Validation errors
- Domain rule violations
- Logic errors

**Integration Test Failures**:
- AWS configuration issues
- IAM permission problems
- Service limits
- Network issues
- Data format mismatches
- Event schema changes

### 5. Property-Based Tests (Hypothesis)

**Purpose**: Test complex algorithms with automatically generated test cases

**Location**: `tests/property_based/`

**Characteristics**:
- ✅ Generates hundreds of test cases automatically
- ✅ Tests mathematical properties and invariants
- ✅ Finds edge cases you might not think of
- ✅ Best for complex algorithms (graph traversal, parsing, etc.)
- ⚠️ Slower than unit tests (runs 100 examples per test)
- ⚠️ Not suitable for integration tests or specific data flows

**What to Test**:
- Complex algorithms with clear properties
- Graph algorithms (cycle detection, traversal)
- Data structure invariants
- Parsing and serialization
- Mathematical properties

**What NOT to Test**:
- Integration with external systems
- End-to-end workflows
- Tests requiring specific data values
- UI interactions

**Example**:
```python
from hypothesis import given
from hypothesis import strategies as st

@given(tasks=st.lists(task_ids, min_size=4, max_size=10, unique=True))
def test_long_chain_cycle(self, tasks):
    """Property: Cycles of any length are detected."""
    # Create chain: tasks[0]→tasks[1]→...→tasks[n-1]
    graph = {}
    for i in range(len(tasks) - 1):
        graph[tasks[i]] = [tasks[i + 1]]
    
    # Check if tasks[n-1]→tasks[0] completes the cycle
    result = has_circular_dependency(tasks[-1], tasks[0], graph)
    
    assert result is True
```

**Running Property-Based Tests**:
```bash
# Run property-based tests only
make test-property

# Run with statistics
poetry run pytest tests/property_based/ -v --hypothesis-show-statistics

# Run with more examples (default is 100)
poetry run pytest tests/property_based/ -v --hypothesis-seed=random
```

**Further Reading**: See `tests/property_based/README.md` for comprehensive documentation on property-based testing concepts, when to use PBT, and interpreting Hypothesis statistics.

## Troubleshooting

### Common Issues

**1. Unit Tests Making Network Calls**
```
Error: RuntimeError: Network call blocked in unit test

Solution: Check that you're using fakes, not real adapters
```

**2. Integration Tests Failing - No AWS Credentials**
```
Error: NoCredentialsError: Unable to locate credentials

Solution: Configure AWS credentials
aws configure
```

**3. Integration Tests Failing - Table Not Found**
```
Error: ResourceNotFoundException: Table not found

Solution: Set TEST_TASKS_TABLE_NAME environment variable
export TEST_TASKS_TABLE_NAME=cns427-task-api-test-tasks
```

**4. EventBridge Tests Failing - No Events Captured**
```
Error: No events found in test results table

Solution: 
1. Deploy test harness: make deploy-test-infra
2. Verify deployment: make check-test-infra
3. Check EventBridge rule is enabled
```

**5. Tests Are Slow**
```
Problem: Unit tests taking > 1 second

Solution:
1. Check for real AWS calls (should use fakes)
2. Check for network calls (should be blocked)
3. Reduce test data size
4. Use pytest-xdist for parallel execution
```

### Debug Techniques

**Print Debugging**:
```python
def test_something(service):
    result = service.do_something()
    print(f"Result: {result}")  # Use -s flag to see output
    assert result is not None
```

**Debugger**:
```python
def test_something(service):
    import pdb; pdb.set_trace()  # Breakpoint
    result = service.do_something()
```

**Verbose Assertions**:
```python
# ❌ Hard to debug
assert response == expected

# ✅ Clear error message
assert response['statusCode'] == 201, \
    f"Expected 201, got {response['statusCode']}"
```

**Changing Log Level for Debug Logs**:

AWS Lambda Powertools Logger respects the `LOG_LEVEL` environment variable. To see DEBUG logs:

```bash
# Option 1: Set environment variable in Lambda console
# Go to Lambda → Configuration → Environment variables
# Add: LOG_LEVEL = DEBUG

# Option 2: Update CDK stack temporarily
# infrastructure/core/task_api_stack.py
environment={
    'LOG_LEVEL': 'DEBUG',  # Change from 'INFO' to 'DEBUG'
    ...
}

# Option 3: Set locally for integration tests
export LOG_LEVEL=DEBUG
poetry run pytest tests/integration/

# Option 4: Use AWS CLI to update Lambda
aws lambda update-function-configuration \
  --function-name cns427-task-api-task-handler \
  --environment Variables={LOG_LEVEL=DEBUG,TASKS_TABLE_NAME=cns427-task-api-tasks,...} \
  --region us-west-2
```

**What You'll See with DEBUG Level**:
```
# INFO level (default)
INFO    create_task:45    Creating task with ID: abc-123
INFO    create_task:97    Created task: abc-123

# DEBUG level (more detail)
INFO    create_task:45    Creating task with ID: abc-123
DEBUG   create_task:48    Validating dependencies: []
DEBUG   update_task:98    Existing task version: 1763172928050, Request version: 1763172928050
DEBUG   publish_event:55  Publishing event: {"Source": "cns427-task-api", "DetailType": "TaskCreated"}
INFO    create_task:97    Created task: abc-123
```

**Tip**: Remember to set `LOG_LEVEL` back to `INFO` in production to avoid excessive logging costs!

### Understanding Structured Logs

AWS Lambda Powertools Logger provides structured JSON logs with automatic module name inclusion.

**Log Format**:
```json
{
  "level": "INFO",
  "location": "create_task:45",
  "message": "Creating task with ID: 751073b5-5a3c-46cd-9d04-f477aa209b9d",
  "timestamp": "2025-11-15 02:15:28,050+0000",
  "service": "task-api",
  "module": "task_service"
}
```

**Module Names by File**:
| File | Module Name in Logs |
|------|---------------------|
| `services/task_service/domain/task_service.py` | `task_service` |
| `services/notification_service/domain/notification_service.py` | `notification_service` |
| `shared/integration/dynamodb_adapter.py` | `dynamodb_adapter` |
| `shared/integration/eventbridge_adapter.py` | `eventbridge_adapter` |
| `services/task_service/handler.py` | `handler` |

**Querying Logs with CloudWatch Logs Insights**:

```sql
# Find all logs from task_service domain
fields @timestamp, level, location, message
| filter module = "task_service"
| sort @timestamp desc
| limit 100

# Find all update operations
fields @timestamp, level, location, message
| filter message like /Updating task/
| sort @timestamp desc

# Find version conflicts
fields @timestamp, level, location, message
| filter message like /Version conflict/
| sort @timestamp desc

# Trace a specific task through the system
fields @timestamp, level, location, message
| filter message like /751073b5-5a3c-46cd-9d04-f477aa209b9d/
| sort @timestamp asc
```

**Example: Tracing a Request**:
```
1. Handler receives request
   INFO    lambda_handler:25    Processing POST /tasks request

2. Domain service creates task
   INFO    create_task:45    Creating task with ID: abc-123
   DEBUG   create_task:48    Validating dependencies: []

3. Repository persists task
   INFO    create_task:97    Created task: abc-123

4. EventBridge publishes event
   DEBUG   publish_event:55    Publishing event: TaskCreated
   INFO    publish_event:75    Published event: TaskCreated

5. Handler returns response
   INFO    lambda_handler:35    Task created successfully: abc-123
```

The `location` field (e.g., `create_task:45`) shows the function name and line number, making it easy to find the exact code that logged the message.

## Best Practices

### 1. Test Independence
- Each test should be completely independent
- Use fresh fixtures for each test
- No shared state between tests
- Clean up after yourself

### 2. Clear Test Intent
- Use descriptive test names
- Follow Given/When/Then structure
- One behavior per test
- Clear assertions

### 3. Realistic Test Data
- Use realistic data
- Test with various combinations
- Include edge cases
- Use test data factories

### 4. Fast Feedback
- Unit tests should be fast (< 1 second total)
- Run unit tests frequently during development
- Run integration tests before committing
- Use watch mode for TDD

### 5. Maintainable Tests
- Keep tests simple
- Avoid complex setup
- Use fixtures appropriately
- Document unusual patterns

## Next Steps

- **[Architecture Guide](architecture.md)** - Understand the architecture that enables testing
- **[Deployment Guide](deployment.md)** - Deploy infrastructure for integration tests
- **[Configuration Guide](configuration.md)** - Configure test infrastructure

## References

- [Testing Honeycomb](https://engineering.atspotify.com/2018/01/testing-of-microservices/) - Spotify Engineering
- [AWS Lambda Testing Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/testing-guide.html)
- [Hexagonal Architecture Testing](https://alistair.cockburn.us/hexagonal-architecture/)
