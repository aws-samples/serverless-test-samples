# Unit Tests

This directory contains unit tests that test individual components in isolation using **in-memory fakes** instead of mocks. This approach provides realistic behavior while maintaining fast execution and easy debugging.

## Overview

Unit tests validate individual components without external dependencies:
- **Domain Logic** - Business rules and validation
- **Lambda Handlers** - Request/response processing
- **Data Models** - Validation and serialization
- **Event Contracts** - Schema compliance and consumer requirements
- **In-Memory Fakes** - Realistic behavior without AWS services

## Test Philosophy

### In-Memory Fakes Over Mocks
- **Real Implementations**: Use actual business logic with in-memory storage
- **No Mock Setup**: Avoid complex mock configuration and verification  
- **Realistic Behavior**: Fakes behave like real dependencies
- **Easy Debugging**: Real data flow makes issues easier to trace

## Test Structure

```
tests/unit/
├── conftest.py                      # Shared fixtures
├── domain/                          # Domain logic tests
│   ├── test_business_rules.py       # Business rule validation
│   ├── test_notification_service.py # Notification domain logic
│   └── test_task_service.py         # Task domain service
├── handlers/                        # Lambda handler tests
│   ├── test_notification_handler.py # Event processing handler
│   └── test_task_handler.py         # API request handler
├── models/                          # Data model tests
│   ├── test_event_contracts.py      # Event schema validation
│   └── test_task_model.py           # Task domain model
└── test_helpers.py                  # Test utility functions
```

## Test Categories

### 1. Domain Tests (`domain/`)

#### Business Rules (`test_business_rules.py`)
**Purpose**: Test business rule validation in isolation

**Coverage**:
- ✅ Circular dependency detection
- ✅ Status transition validation
- ✅ Priority validation
- ✅ Dependency chain validation
- ✅ Business constraint enforcement

#### Task Service (`test_task_service.py`)
**Purpose**: Test core domain service logic

**Coverage**:
- ✅ CRUD operations
- ✅ Business rule enforcement
- ✅ Event publishing
- ✅ Error handling
- ✅ Data transformations

#### Notification Service (`test_notification_service.py`)
**Purpose**: Test notification domain logic

**Coverage**:
- ✅ Event processing
- ✅ Notification formatting
- ✅ Error handling
- ✅ Event type routing

### 2. Handler Tests (`handlers/`)

#### Task Handler (`test_task_handler.py`)
**Purpose**: Test Lambda handler with realistic API Gateway events

**Approach**:
- Use real `lambda_handler` function with actual API Gateway event structure
- Inject in-memory fakes for repository and event publisher
- Test complete request → domain → response flow

**Coverage**:
- ✅ HTTP status codes (201, 200, 204, 400, 404, 500)
- ✅ Request parsing and validation
- ✅ Response formatting
- ✅ Error handling
- ✅ Data persistence verification
- ✅ Event publishing verification

**Example Test**:
```python
def test_create_task_returns_201(self, task_service, lambda_context):
    # GIVEN realistic API Gateway event
    event = create_api_gateway_event(
        method="POST",
        path="/tasks",
        body={"title": "Test Task", "priority": "high"}
    )
    
    # WHEN processing through real handler
    with patch('services.task_service.handler.task_service', task_service):
        response = lambda_handler(event, lambda_context)
    
    # THEN verify HTTP response
    assert response["statusCode"] == 201
    body = json.loads(response["body"])
    assert body["title"] == "Test Task"
    assert body["priority"] == "high"
```

#### Notification Handler (`test_notification_handler.py`)
**Purpose**: Test event processing handler

**Coverage**:
- ✅ EventBridge event parsing
- ✅ Notification processing logic
- ✅ Error handling
- ✅ Event type routing

### 3. Model Tests (`models/`)

#### Task Model (`test_task_model.py`)
**Purpose**: Test task domain model and validation

**Coverage**:
- ✅ Model creation and validation
- ✅ Field constraints and validation rules
- ✅ Serialization/deserialization
- ✅ Model methods and properties
- ✅ Status and priority enums
- ✅ Dependency management

#### Event Contracts (`test_event_contracts.py`)
**Purpose**: Test event schema compliance and consumer requirements

**What are Consumer-Driven Contract Tests?**

Consumer-driven contract tests are owned by the **consumer** (subscriber) of events, not the producer (publisher). They validate that:
1. Events contain all fields the consumer needs
2. Field types and formats match consumer expectations
3. EventBridge rule patterns correctly route events
4. Schema changes don't break downstream consumers

**When to Use Contract Tests:**

Contract tests become critical in **event-driven architectures** with:
- **Multiple teams** managing different publishers and subscribers
- **Unknown subscribers** where the publisher doesn't know all consumers
- **Rapidly evolving schemas** where producers change events frequently
- **Loose coupling** where consumers may not use all event fields

**When NOT to Use Contract Tests:**

For this Task API application, contract tests are **less critical** because:
- **Single team ownership**: Task service and notification service owned by same team
- **Known consumers**: Publisher knows all subscribers
- **Coordinated changes**: Schema changes can be synchronized across services
- **Business impact**: Breaking changes have low business impact

In real-world scenarios, evaluate:
- **Team boundaries**: Different teams = higher value for contract tests
- **Business impact**: Critical consumers = invest in contract tests
- **Change frequency**: Rapid evolution = contract tests prevent breakage
- **Coupling**: Tight coupling = less need for contract tests

**Running Contract Tests in CI/CD:**

Contract tests should run in the **producer's pipeline** to catch breaking changes before deployment:

```yaml
# Producer pipeline (Task Service)
- name: Run Contract Tests
  run: poetry run pytest tests/unit/models/test_event_contracts.py -v
  
- name: Validate EventBridge Rule Patterns
  run: poetry run pytest tests/unit/models/test_event_contracts.py::TestEventContracts::test_eventbridge_rule_pattern_matching -v
```

**Coverage**:
- ✅ Schema validation using Pydantic
- ✅ Consumer-specific field requirements
- ✅ EventBridge rule pattern matching
- ✅ Schema drift detection
- ✅ Breaking change prevention

**Test Scenarios**:

1. **Schema Validation**: Ensures events match expected structure
   ```python
   def test_schema_validation(self):
       # Validates TaskCreated event has all required fields
       # with correct types (string, enum, list, etc.)
   ```

2. **Consumer Contracts**: Validates consumer-specific needs
   ```python
   def test_consumer_contract_notification_service(self):
       # Ensures notification service gets task_id, title, status
   ```

3. **Rule Pattern Matching**: Validates EventBridge routing
   ```python
   def test_eventbridge_rule_pattern_matching(self):
       # Ensures events match rule patterns for correct routing
   ```

4. **Contract Violation Detection**: Catches breaking changes
   ```python
   def test_contract_violation_detection(self):
       # Detects missing fields, wrong types, invalid enums
   ```

## In-Memory Fakes

Located in `tests/shared/fakes/`, these provide realistic behavior without AWS dependencies.

### `InMemoryTaskRepository`
Simulates DynamoDB operations with in-memory dictionary storage.

**Features**:
- Full CRUD operations
- Optimistic locking with version checking
- Pagination simulation
- Error conditions (duplicates, version conflicts)
- Helper methods for test verification

**Usage**:
```python
from tests.shared.fakes.in_memory_task_repository import InMemoryTaskRepository

@pytest.fixture
def repository():
    return InMemoryTaskRepository()

def test_create_task(self, repository):
    task = Task(title="Test Task")
    result = repository.create_task(task)
    
    assert result == task
    assert len(repository.tasks) == 1
```

### `InMemoryEventPublisher`
Simulates EventBridge publishing by capturing events in memory.

**Features**:
- Captures published events in list
- Event filtering and verification methods
- No actual EventBridge calls
- Helper methods for assertions

**Usage**:
```python
from tests.shared.fakes.in_memory_event_publisher import InMemoryEventPublisher

@pytest.fixture
def publisher():
    return InMemoryEventPublisher()

def test_event_publishing(self, publisher):
    publisher.publish_event(event_data)
    
    assert len(publisher.events) == 1
    assert publisher.events[0]['DetailType'] == 'TaskCreated'
```

### `InMemoryNotificationService`
Simulates notification processing by storing notifications in memory.

**Features**:
- Captures processed events and notifications
- Categorizes notifications by type
- Verification methods for test assertions

**Usage**:
```python
from tests.shared.fakes.in_memory_notification_service import InMemoryNotificationService

@pytest.fixture
def notification_service():
    return InMemoryNotificationService()

def test_notification(self, notification_service):
    notification_service.process_event(event)
    
    assert len(notification_service.notifications) == 1
```

## Running Tests

### All Unit Tests
```bash
# Using Make
make test-unit

# Or using pytest directly
poetry run pytest tests/unit -v

# Or using test script
poetry run python scripts/testing.py --type unit
```

### Specific Test Categories
```bash
# Domain tests
poetry run pytest tests/unit/domain -v

# Handler tests
poetry run pytest tests/unit/handlers -v

# Model tests
poetry run pytest tests/unit/models -v
```

### Specific Test Files
```bash
# Business rules
poetry run pytest tests/unit/domain/test_business_rules.py -v

# Task service
poetry run pytest tests/unit/domain/test_task_service.py -v

# Task handler
poetry run pytest tests/unit/handlers/test_task_handler.py -v

# Event contracts
poetry run pytest tests/unit/models/test_event_contracts.py -v

# Task model
poetry run pytest tests/unit/models/test_task_model.py -v
```

### Specific Test Methods
```bash
# Run specific test method
poetry run pytest tests/unit/models/test_event_contracts.py::TestEventContracts::test_schema_validation -v

# Run tests matching pattern
poetry run pytest tests/unit -k "contract" -v
```

### With Coverage
```bash
# Generate coverage report
poetry run pytest tests/unit --cov=services --cov=shared --cov-report=html

# View coverage report
open htmlcov/index.html

# Show missing lines
poetry run pytest tests/unit --cov=services --cov=shared --cov-report=term-missing
```

### With Verbose Output
```bash
# See detailed test output
poetry run pytest tests/unit -v -s

# Stop on first failure
poetry run pytest tests/unit -v -x
```

## Test Patterns

### Test Structure
All tests follow the **Given/When/Then** pattern:

```python
def test_behavior_description(self, fixtures):
    # GIVEN - Setup test data and conditions
    setup_data = create_test_data()
    
    # WHEN - Execute the behavior being tested
    result = component_under_test.method(setup_data)
    
    # THEN - Assert expected outcomes
    assert result.status == expected_status
    assert result.data == expected_data
    
    # AND - Verify side effects (optional)
    assert fake_dependency.was_called_correctly()
```

### Test Naming Convention
- **Files**: `test_{component_name}.py`
- **Classes**: `Test{ComponentName}`
- **Methods**: `test_{behavior}_returns_{expected_result}`

**Examples**:
- `test_create_task_returns_201`
- `test_get_nonexistent_task_returns_404`
- `test_validation_error_returns_400`
- `test_update_task_with_version_conflict_raises_error`

### Fixture Usage
```python
@pytest.fixture
def repository():
    """Create fresh in-memory repository for each test."""
    return InMemoryTaskRepository()

@pytest.fixture
def publisher():
    """Create fresh in-memory publisher for each test."""
    return InMemoryEventPublisher()

@pytest.fixture
def task_service(repository, publisher):
    """Create task service with in-memory dependencies."""
    return TaskService(repository, publisher)
```

## Test Data Creation

### Helper Functions
```python
def create_api_gateway_event(
    method: str = "GET",
    path: str = "/tasks",
    body: Optional[Dict] = None,
    query_params: Optional[Dict] = None,
    path_params: Optional[Dict] = None
) -> Dict[str, Any]:
    """Create realistic API Gateway event for testing."""
    return {
        "httpMethod": method,
        "path": path,
        "pathParameters": path_params or {},
        "queryStringParameters": query_params or {},
        "body": json.dumps(body) if body else None,
        "headers": {"Content-Type": "application/json"},
        "requestContext": {"requestId": "test-123", "stage": "test"}
    }
```

### Test Data Factories
```python
def create_test_task(title: str = "Test Task", **kwargs) -> Task:
    """Create a test task with default values."""
    defaults = {
        "title": title,
        "description": "Test description",
        "priority": TaskPriority.MEDIUM,
        "status": TaskStatus.PENDING
    }
    defaults.update(kwargs)
    return Task(**defaults)
```

## Coverage Requirements

### Minimum Coverage
- **Overall**: 80% minimum (enforced by pytest configuration)
- **Per File**: Aim for 90%+ coverage on critical components
- **Branches**: Include both positive and negative test cases

### Coverage Report
```bash
# Generate detailed coverage report
poetry run pytest tests/unit --cov=task_api --cov-report=html --cov-report=term-missing

# View missing lines
poetry run pytest tests/unit --cov=task_api --cov-report=term-missing
```

## Best Practices

### 1. Test Independence
- Each test should be completely independent
- Use fresh fixtures for each test
- No shared state between tests
- Clean setup and teardown

### 2. Clear Test Intent
- Use descriptive test names that explain the behavior
- Follow Given/When/Then structure
- Test one behavior per test method
- Clear assertions with meaningful error messages

### 3. Comprehensive Testing
- Test both happy path and error scenarios
- Include edge cases and boundary conditions
- Verify side effects and state changes
- Test validation and error messages

### 4. Realistic Test Data
- Use realistic data that represents actual usage
- Test with various data combinations
- Include both valid and invalid scenarios
- Use consistent test data creation patterns

## Debugging Tests

### Common Issues

**Test Isolation Problems**
```python
# Problem: Shared state between tests
class TestExample:
    shared_data = []  # DON'T DO THIS
    
    def test_one(self):
        self.shared_data.append("item")
        assert len(self.shared_data) == 1
    
    def test_two(self):
        # This might fail if test_one ran first
        assert len(self.shared_data) == 0

# Solution: Use fixtures
@pytest.fixture
def fresh_data():
    return []

def test_one(fresh_data):
    fresh_data.append("item")
    assert len(fresh_data) == 1
```

**Assertion Errors**
```python
# Problem: Unclear assertion errors
assert response == expected  # Hard to debug when it fails

# Solution: Specific assertions with messages
assert response["statusCode"] == 201, f"Expected 201, got {response['statusCode']}"
assert response["body"]["title"] == "Test Task"
```

### Debug Mode
```bash
# Run with verbose output and stop on first failure
poetry run pytest tests/unit -v -x

# Run with pdb debugger on failures
poetry run pytest tests/unit --pdb

# Run specific test with output
poetry run pytest tests/unit/test_task_handler.py::TestTaskHandler::test_create_task_returns_201 -v -s
```

## Performance

### Test Execution Speed
- **Target**: < 1 second for all unit tests
- **Actual**: ~100-500ms typical execution time
- **Factors**: In-memory operations, no network calls, minimal setup

### Optimization Tips
- Use fixtures efficiently (session, module, function scope)
- Avoid unnecessary test data creation
- Keep fakes simple and focused
- Run tests in parallel when possible

## Troubleshooting

### Common Issues

**Import Errors**
```
Error: ModuleNotFoundError: No module named 'services'
Solution: Ensure you're running from project root and dependencies are installed
```

```bash
# Install dependencies
poetry install

# Run from project root
cd /path/to/project
poetry run pytest tests/unit
```

**Fixture Not Found**
```
Error: fixture 'task_service' not found
Solution: Check conftest.py for fixture definitions
```

```bash
# Check available fixtures
poetry run pytest tests/unit --fixtures

# Verify fixture scope and location
cat tests/unit/conftest.py
```

**Pydantic Validation Errors in Contract Tests**
```
Error: ValidationError: 1 validation error for TaskDetailSchema
Solution: Event schema doesn't match contract - this is expected behavior for drift detection
```

This is intentional for `test_contract_violation_detection` - it validates that schema changes are caught.

**Test Isolation Issues**
```
Error: Test passes alone but fails when run with others
Solution: Ensure proper fixture cleanup and no shared state
```

```python
# Use fresh fixtures for each test
@pytest.fixture
def repository():
    return InMemoryTaskRepository()  # New instance each time

# Avoid class-level shared state
class TestExample:
    shared_data = []  # DON'T DO THIS
```

### Debug Mode
```bash
# Run with verbose output and stop on first failure
poetry run pytest tests/unit -v -x

# Run with pdb debugger on failures
poetry run pytest tests/unit --pdb

# Run specific test with output
poetry run pytest tests/unit/models/test_event_contracts.py::TestEventContracts::test_schema_validation -v -s
```

### Performance Issues
```bash
# Check slow tests
poetry run pytest tests/unit --durations=10

# Run tests in parallel (if installed pytest-xdist)
poetry run pytest tests/unit -n auto
```

## Best Practices

### 1. Test Independence
- Each test should be completely independent
- Use fresh fixtures for each test
- No shared state between tests
- Clean setup and teardown

### 2. Clear Test Intent
- Use descriptive test names that explain the behavior
- Follow Given/When/Then structure
- Test one behavior per test method
- Clear assertions with meaningful error messages

### 3. Comprehensive Testing
- Test both happy path and error scenarios
- Include edge cases and boundary conditions
- Verify side effects and state changes
- Test validation and error messages

### 4. Realistic Test Data
- Use realistic data that represents actual usage
- Test with various data combinations
- Include both valid and invalid scenarios
- Use consistent test data creation patterns

## Contributing

### Adding New Tests
1. **Choose the right category**: domain, handlers, or models
2. **Follow naming conventions**: `test_{behavior}_returns_{expected_result}`
3. **Use appropriate fixtures**: Defined in `conftest.py`
4. **Include both positive and negative cases**
5. **Add docstrings** explaining test purpose
6. **Ensure test independence**: No shared state

### Adding Event Contract Tests
When adding new event types:

1. **Define Pydantic schema** in `test_event_contracts.py`:
   ```python
   class NewEventDetailSchema(BaseModel):
       field1: str
       field2: int
   ```

2. **Update validation function** to handle new event type

3. **Add schema validation test**:
   ```python
   def test_new_event_schema_validation(self):
       # Test event matches schema
   ```

4. **Add consumer contract test** if needed:
   ```python
   def test_consumer_contract_for_new_event(self):
       # Test consumer-specific requirements
   ```

5. **Update rule pattern test** if routing changes

### Updating In-Memory Fakes
When updating fakes in `tests/shared/fakes/`:

1. **Keep behavior consistent** with real AWS services
2. **Update all affected tests**
3. **Add tests for new fake functionality**
4. **Document any behavior differences**
5. **Maintain simplicity** - fakes should be simple and focused

### Test Review Checklist
- [ ] Tests are independent and isolated
- [ ] Clear test names and documentation
- [ ] Both positive and negative cases covered
- [ ] Appropriate use of fixtures
- [ ] Realistic test data
- [ ] Clear assertions with good error messages
- [ ] No external dependencies
- [ ] Fast execution (< 1 second total)
- [ ] Contract tests run in producer pipeline (if applicable)

## When Contract Tests Matter

### High Value Scenarios
Contract tests provide significant value when:

1. **Multiple Teams**: Different teams own publishers and subscribers
   - Team A owns Task Service (publisher)
   - Team B owns Analytics Service (subscriber)
   - Team C owns Audit Service (subscriber)
   - Contract tests prevent Team A from breaking Teams B and C

2. **Unknown Subscribers**: Publisher doesn't know all consumers
   - Event bus pattern with dynamic subscription
   - Third-party integrations
   - Future services not yet built
   - Contract tests document what consumers can depend on

3. **Rapid Evolution**: Producer changes events frequently
   - Adding new fields (usually safe)
   - Removing fields (breaking change)
   - Changing field types (breaking change)
   - Contract tests catch breaking changes before deployment

4. **High Business Impact**: Breaking changes affect critical systems
   - Payment processing
   - Security auditing
   - Compliance reporting
   - Contract tests prevent production incidents

### Low Value Scenarios
Contract tests provide less value when:

1. **Single Team Ownership**: Same team owns publisher and subscribers
   - This Task API application (task service + notification service)
   - Changes can be coordinated across services
   - Team knows all consumers and their requirements

2. **Known Consumers**: Publisher knows all subscribers
   - Direct service-to-service communication
   - Tightly coupled services
   - Small number of well-known consumers

3. **Stable Schemas**: Events rarely change
   - Mature APIs with stable contracts
   - Backward compatibility maintained
   - Versioned events

4. **Low Business Impact**: Breaking changes have minimal consequences
   - Internal development tools
   - Non-critical notifications
   - Easily recoverable failures

### Decision Framework

Ask these questions to decide if contract tests are worth the investment:

1. **Who owns the services?**
   - Same team → Lower priority
   - Different teams → Higher priority

2. **How many consumers?**
   - 1-2 known consumers → Lower priority
   - Many or unknown consumers → Higher priority

3. **How often do schemas change?**
   - Rarely → Lower priority
   - Frequently → Higher priority

4. **What's the business impact of breakage?**
   - Low impact → Lower priority
   - High impact → Higher priority

5. **Can changes be coordinated?**
   - Yes, easily → Lower priority
   - No, difficult → Higher priority

### Implementation Strategy

If contract tests are valuable for your use case:

1. **Consumer-owned tests**: Each consumer writes their own contract tests
2. **Run in producer pipeline**: Catch breaking changes before deployment
3. **Version events**: Use semantic versioning for event schemas
4. **Document contracts**: Clear documentation of what consumers can depend on
5. **Gradual rollout**: Add contract tests incrementally, starting with critical consumers

## Performance

Unit tests are designed for speed:

- **Target**: < 1 second for all unit tests
- **Actual**: ~100-500ms typical execution time
- **Factors**: In-memory operations, no network calls, minimal setup

### Optimization Tips
- Use fixtures efficiently (session, module, function scope)
- Avoid unnecessary test data creation
- Keep fakes simple and focused
- Run tests in parallel when possible

## Next Steps

- **[Integration Tests](../integration/README.md)** - Test with real AWS services
- **[E2E Tests](../e2e/README.md)** - Test complete workflows
- **[Testing Guide](../../docs/testing-guide.md)** - Overall testing strategy
- **[Architecture Guide](../../docs/architecture.md)** - Understand the system design