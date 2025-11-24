# Architecture Guide

This document provides a deep dive into the hexagonal architecture pattern used in this serverless application and explains how it enables comprehensive testing.

## Table of Contents

- [Overview](#overview)
- [Monorepo Service Pattern](#monorepo-service-pattern)
- [The Problem: Monolithic Lambda](#the-problem-monolithic-lambda)
- [The Solution: Hexagonal Architecture](#the-solution-hexagonal-architecture)
- [Layer Details](#layer-details)
- [Dependency Flow](#dependency-flow)
- [Benefits for Testing](#benefits-for-testing)
- [Implementation Patterns](#implementation-patterns)

## Overview

This application uses a **monorepo service pattern** where each service implements **hexagonal architecture** (also known as ports and adapters). This combination provides:

- **Service Boundaries**: Each service is a complete, independent hexagon
- **Testable**: Business logic can be tested without AWS
- **Maintainable**: Changes to AWS services don't affect business logic
- **Flexible**: Easy to swap implementations (real AWS, fakes, mocks)
- **Clear**: Each layer has a single responsibility
- **Optimized Packaging**: Each Lambda only includes its service code

## Monorepo Service Pattern

### Why Services, Not Shared Modules?

Each service is a **complete hexagon** with its own domain, models, and handler. Only infrastructure adapters are shared.

```
services/
├── task_service/              # Complete hexagon #1
│   ├── handler.py            # Entry point
│   ├── domain/               # Business logic
│   │   ├── task_service.py
│   │   ├── business_rules.py
│   │   └── exceptions.py
│   ├── models/               # Domain models
│   │   ├── task.py
│   │   └── api.py
│   └── requirements.txt      # Service dependencies
│
├── notification_service/      # Complete hexagon #2
│   ├── handler.py            # Entry point
│   ├── domain/               # Business logic
│   │   └── notification_service.py
│   └── requirements.txt      # Service dependencies
│
shared/                        # Shared infrastructure only
└── integration/              # Reusable adapters
    ├── dynamodb_adapter.py
    └── eventbridge_adapter.py
```

### Service Boundaries Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      TASK SERVICE HEXAGON                       │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐   │
│  │                    handler.py                          │   │
│  │              (Lambda Entry Point)                      │   │
│  └────────────────────────────────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│  ┌────────────────────────────────────────────────────────┐   │
│  │                  domain/                               │   │
│  │  • task_service.py (orchestration)                     │   │
│  │  • business_rules.py (validation)                      │   │
│  │  • exceptions.py (domain errors)                       │   │
│  └────────────────────────────────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│  ┌────────────────────────────────────────────────────────┐   │
│  │                  models/                               │   │
│  │  • task.py (Task, TaskStatus, events)                  │   │
│  │  • api.py (API request/response models)                │   │
│  └────────────────────────────────────────────────────────┘   │
│                            │                                    │
└────────────────────────────┼────────────────────────────────────┘
                             │
                             │ Uses shared adapters
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   SHARED INFRASTRUCTURE                         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐   │
│  │            shared/integration/                         │   │
│  │  • dynamodb_adapter.py (persistence)                   │   │
│  │  • eventbridge_adapter.py (events)                     │   │
│  │  • interfaces.py (protocols)                           │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                             │
                             │ Uses shared adapters
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                 NOTIFICATION SERVICE HEXAGON                    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐   │
│  │                    handler.py                          │   │
│  │              (Lambda Entry Point)                      │   │
│  └────────────────────────────────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│  ┌────────────────────────────────────────────────────────┐   │
│  │                  domain/                               │   │
│  │  • notification_service.py (event processing)          │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Why Each Service is a Complete Hexagon

**Task Service** owns:
- Task creation, updates, deletion logic
- Task validation and business rules
- Task domain models and events
- API request/response contracts

**Notification Service** owns:
- Event processing logic
- Notification routing
- Event-specific business rules

**Shared Infrastructure** provides:
- DynamoDB adapter (used by both services)
- EventBridge adapter (used by both services)
- Protocol interfaces

### Example Imports for Each Service

**Task Service** (`services/task_service/handler.py`):
```python
# Service-specific imports
from services.task_service.domain.task_service import TaskService
from services.task_service.models.task import Task, TaskStatus
from services.task_service.models.api import CreateTaskRequest

# Shared infrastructure imports
from shared.integration.dynamodb_adapter import DynamoDBTaskRepository
from shared.integration.eventbridge_adapter import EventBridgePublisher
```

**Notification Service** (`services/notification_service/handler.py`):
```python
# Service-specific imports
from services.notification_service.domain.notification_service import NotificationService

# Shared infrastructure imports (if needed)
from shared.integration.eventbridge_adapter import EventBridgePublisher
```

**Shared Integration** (`shared/integration/dynamodb_adapter.py`):
```python
# Can import from any service's models
from services.task_service.models.task import Task, TaskStatus

# Implements shared protocols
from shared.integration.interfaces import TaskRepositoryProtocol
```

### Shared Infrastructure vs Service-Specific Code

**Shared Infrastructure** (`shared/`):
- Infrastructure adapters (DynamoDB, EventBridge)
- Protocol interfaces
- AWS SDK interactions
- Error handling utilities
- **Reason**: Reusable across services, no business logic

**Service-Specific Code** (`services/*/`):
- Domain logic and business rules
- Domain models and events
- API contracts
- Service orchestration
- **Reason**: Belongs to bounded context, service-specific

### Benefits of This Pattern

1. **Independent Deployment**
   - Each service can be deployed separately
   - Changes to one service don't affect others
   - Faster CI/CD pipelines

2. **Optimized Lambda Packages**
   - Task service Lambda: ~30% smaller (no notification code)
   - Notification service Lambda: ~40% smaller (no API/models)
   - Faster cold starts

3. **Clear Bounded Contexts**
   - Each service has clear responsibilities
   - Domain models belong to their service
   - Easy to understand ownership

4. **Scalable Testing**
   - Test services in isolation
   - Shared adapters tested once
   - Integration tests verify service boundaries

5. **Team Scalability**
   - Different teams can own different services
   - Clear interfaces between services
   - Reduced merge conflicts

### Cross-Service Communication

Services communicate through **events**, not by sharing domain models. This maintains loose coupling while enabling collaboration.

**Pattern: Event-Based Communication**

```
Task Service (Publisher)          Notification Service (Subscriber)
     │                                      │
     │ 1. Creates TaskEvent                │
     │    (owns the model)                 │
     │                                      │
     │ 2. to_eventbridge_entry()           │
     │    ↓                                 │
     │  EventBridge                         │
     │    ↓                                 │
     │                3. from_eventbridge_event()
     │                                      │
     │                4. Processes event    │
     │                   (doesn't need Task model)
```

**Key Principle: Domain Ownership**

- **Task models stay in Task Service** - They belong to that bounded context
- **Events are the contract** - Services communicate via event structure, not domain models
- **Loose coupling** - Notification Service doesn't depend on Task internals

**Example: TaskEvent Model** (`services/task_service/models/task.py`):

```python
@dataclass
class TaskEvent:
    """Event model with bidirectional conversion."""
    
    def to_eventbridge_entry(self, event_bus_name: str = None) -> Dict[str, Any]:
        """Convert to EventBridge format for publishing."""
        return {
            'Source': self.source,
            'DetailType': self.event_type,
            'Detail': json.dumps(self.task_data),
            'EventBusName': event_bus_name
        }
    
    @classmethod
    def from_eventbridge_event(cls, event: Dict[str, Any]) -> 'TaskEvent':
        """Parse EventBridge event for consuming."""
        return cls(
            event_type=event.get('detail-type', '').replace('TEST-', ''),
            task_data=event.get('detail', {}),
            source=event.get('source', 'cns427-task-api')
        )
```

**Usage in Notification Service**:

```python
# Notification handler doesn't need Task model
from services.task_service.models.task import TaskEvent  # Only the event!

def lambda_handler(event, context):
    # Parse event using model's utility method
    task_event = TaskEvent.from_eventbridge_event(event)
    
    # Process event data (just a dict, not Task model)
    notification_service.process_task_event(
        task_event.event_type,
        task_event.task_data  # Dict, not Task object
    )
```

**Why This Works**:

✅ **Domain Ownership**: Task Service owns Task model and events  
✅ **Loose Coupling**: Notification Service only depends on event structure  
✅ **Utility Methods**: Event model provides parsing/serialization helpers  
✅ **No Shared Models**: Services don't share domain models, only event contracts  
✅ **Testability**: Easy to test event parsing independently  

**What NOT to Do**:

❌ **Don't move models to shared/** - Models belong to their service's bounded context  
❌ **Don't import Task in Notification Service** - Use event data (dict) instead  
❌ **Don't create shared domain models** - Each service owns its domain  

## The Problem: Monolithic Lambda

### Before: Everything Mixed Together

```python
# ❌ BAD: Monolithic Lambda Handler
def lambda_handler(event, context):
    # HTTP parsing
    body = json.loads(event['body'])
    task_id = event['pathParameters']['id']
    
    # Business logic
    if not body.get('title'):
        return {'statusCode': 400, 'body': 'Title required'}
    
    # DynamoDB operations
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('tasks-table')
    table.put_item(Item={
        'task_id': task_id,
        'title': body['title'],
        'status': 'pending'
    })
    
    # EventBridge publishing
    events = boto3.client('events')
    events.put_events(Entries=[{
        'Source': 'task-api',
        'DetailType': 'TaskCreated',
        'Detail': json.dumps({'task_id': task_id})
    }])
    
    # HTTP response
    return {
        'statusCode': 201,
        'body': json.dumps({'task_id': task_id})
    }
```

### Problems with This Approach

1. **Hard to Test**
   - Requires mocking boto3 clients
   - Complex mock setup for each test
   - Mocks don't behave like real AWS services
   - Tests are brittle and break easily

2. **Slow Tests**
   - Must mock AWS SDK for every test
   - Mock setup adds overhead
   - Can't test business logic in isolation

3. **Tight Coupling**
   - Business logic mixed with AWS code
   - Can't change AWS services without changing business logic
   - Hard to understand what the code does

4. **Poor Maintainability**
   - Changes ripple across layers
   - Hard to add new features
   - Difficult to debug

## The Solution: Hexagonal Architecture

### After: Layered Separation

```
┌─────────────────────────────────────────────────────────────┐
│                    HANDLER LAYER                            │
│                  (task_handler.py)                          │
│                                                              │
│  Responsibilities:                                           │
│  • Parse HTTP requests (API Gateway events)                 │
│  • Validate request format                                  │
│  • Delegate to domain layer                                 │
│  • Format HTTP responses                                    │
│  • Handle HTTP errors (400, 404, 500)                       │
│                                                              │
│  Dependencies: Domain services only                         │
│  Testing: Mock API Gateway events, inject fake services    │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Calls
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    DOMAIN LAYER                             │
│              (task_service.py, business_rules.py)           │
│                                                              │
│  Responsibilities:                                           │
│  • Pure business logic                                      │
│  • Business rules and validation                            │
│  • Orchestrate operations                                   │
│  • No AWS dependencies                                      │
│  • No HTTP knowledge                                        │
│                                                              │
│  Dependencies: Protocol interfaces only                     │
│  Testing: In-memory fakes, no AWS required                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Uses protocols
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  INTEGRATION LAYER                          │
│         (dynamodb_adapter.py, eventbridge_adapter.py)       │
│                                                              │
│  Responsibilities:                                           │
│  • Implement protocol interfaces                            │
│  • AWS SDK operations                                       │
│  • Error handling and retries                               │
│  • Data transformation (domain ↔ AWS)                       │
│                                                              │
│  Dependencies: AWS SDK (boto3)                              │
│  Testing: Real AWS services or error-simulating fakes      │
└─────────────────────────────────────────────────────────────┘
```

## Layer Details

### Handler Layer

**Location**: `services/*/handler.py` (one per service)

**Purpose**: Entry point for each Lambda function

**Example - Task Service**:
```python
# services/task_service/handler.py
from services.task_service.domain.task_service import TaskService

# Initialize service (self-initializing pattern)
task_service = TaskService()

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle API Gateway requests."""
    try:
        # Parse HTTP request
        http_method = event['httpMethod']
        path = event['path']
        
        # Route to appropriate handler
        if http_method == 'POST' and path == '/tasks':
            return handle_create_task(event)
        elif http_method == 'GET' and '/tasks/' in path:
            return handle_get_task(event)
        # ... more routes
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def handle_create_task(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle task creation."""
    # Parse request body
    body = json.loads(event['body'])
    
    # Delegate to domain
    task = task_service.create_task(
        title=body['title'],
        description=body.get('description'),
        priority=body.get('priority', 'medium')
    )
    
    # Format response
    return {
        'statusCode': 201,
        'body': json.dumps({
            'task_id': task.task_id,
            'title': task.title,
            'status': task.status
        })
    }
```

**Key Characteristics**:
- ✅ Only knows about HTTP (API Gateway events)
- ✅ Delegates all business logic to domain
- ✅ No AWS SDK calls (except through domain)
- ✅ Simple request/response transformation

### Domain Layer

**Location**: `services/*/domain/` (service-specific)

**Purpose**: Pure business logic with no infrastructure dependencies

**Example - Task Service Domain**:
```python
# services/task_service/domain/task_service.py
from shared.integration.interfaces import (
    TaskRepositoryProtocol,
    EventPublisherProtocol
)
from services.task_service.models.task import Task, TaskStatus

class TaskService:
    """Domain service for task operations."""
    
    def __init__(
        self,
        repository: Optional[TaskRepositoryProtocol] = None,
        event_publisher: Optional[EventPublisherProtocol] = None
    ):
        """Initialize with dependencies (self-initializing pattern)."""
        from shared.integration.dynamodb_adapter import DynamoDBTaskRepository
        from shared.integration.eventbridge_adapter import EventBridgePublisher
        
        self.repository = repository or DynamoDBTaskRepository()
        self.event_publisher = event_publisher or EventBridgePublisher()
    
    def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        priority: str = 'medium'
    ) -> Task:
        """Create a new task."""
        # Business logic: Create task
        task = Task(
            title=title,
            description=description,
            priority=priority,
            status=TaskStatus.PENDING
        )
        
        # Business rule: Validate task
        if not task.title or len(task.title) < 3:
            raise ValueError("Title must be at least 3 characters")
        
        # Persist task
        created_task = self.repository.create_task(task)
        
        # Publish event
        self.event_publisher.publish_task_created(created_task)
        
        return created_task
```

**Key Characteristics**:
- ✅ Pure business logic
- ✅ No AWS SDK imports
- ✅ Uses protocol interfaces
- ✅ Self-initializing with dependency injection support
- ✅ Easy to test with fakes

### Integration Layer

**Location**: `shared/integration/` (shared across services)

**Purpose**: Implement protocol interfaces using AWS services

**Example - Protocol Definition**:
```python
# shared/integration/interfaces.py
from typing import Protocol, Optional, List
from services.task_service.models.task import Task

class TaskRepositoryProtocol(Protocol):
    """Protocol for task persistence."""
    
    def create_task(self, task: Task) -> Task:
        """Create a new task."""
        ...
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        ...
    
    def update_task(self, task: Task) -> Task:
        """Update existing task."""
        ...
    
    def delete_task(self, task_id: str) -> None:
        """Delete task by ID."""
        ...
    
    def list_tasks(self, limit: int = 100) -> List[Task]:
        """List all tasks."""
        ...
```

**Example - DynamoDB Implementation**:
```python
# shared/integration/dynamodb_adapter.py
import boto3
from typing import Optional, List
from services.task_service.models.task import Task
from shared.integration.interfaces import TaskRepositoryProtocol

class DynamoDBTaskRepository:
    """DynamoDB implementation of task repository."""
    
    def __init__(self, table_name: Optional[str] = None):
        """Initialize with DynamoDB table."""
        self.table_name = table_name or os.getenv('TASKS_TABLE_NAME')
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(self.table_name)
    
    def create_task(self, task: Task) -> Task:
        """Create task in DynamoDB."""
        try:
            self.table.put_item(
                Item={
                    'task_id': task.task_id,
                    'title': task.title,
                    'description': task.description,
                    'priority': task.priority,
                    'status': task.status,
                    'version': task.version,
                    'created_at': task.created_at.isoformat(),
                    'updated_at': task.updated_at.isoformat()
                }
            )
            return task
        except ClientError as e:
            # Handle DynamoDB errors
            raise RepositoryError(f"Failed to create task: {e}")
    
    # ... other methods
```

**Key Characteristics**:
- ✅ Implements protocol interfaces
- ✅ Contains all AWS SDK code
- ✅ Handles AWS-specific errors
- ✅ Transforms between domain models and AWS formats

## Dependency Flow

### Production Flow

```
API Gateway Event
       │
       ▼
┌──────────────────┐
│ Lambda Handler   │ ← Entry point
└──────────────────┘
       │
       │ Creates/uses
       ▼
┌──────────────────┐
│ TaskService      │ ← Domain logic
└──────────────────┘
       │
       │ Uses protocols
       ▼
┌──────────────────┐     ┌──────────────────┐
│ DynamoDB Adapter │     │ EventBridge      │
│ (Real AWS)       │     │ Adapter          │
└──────────────────┘     └──────────────────┘
       │                         │
       ▼                         ▼
┌──────────────────┐     ┌──────────────────┐
│ DynamoDB Table   │     │ EventBridge Bus  │
└──────────────────┘     └──────────────────┘
```

### Unit Test Flow

```
Test Code
       │
       ▼
┌──────────────────┐
│ TaskService      │ ← Same domain logic
└──────────────────┘
       │
       │ Inject fakes
       ▼
┌──────────────────┐     ┌──────────────────┐
│ InMemory         │     │ InMemory         │
│ Repository       │     │ Publisher        │
│ (Fake)           │     │ (Fake)           │
└──────────────────┘     └──────────────────┘
       │                         │
       ▼                         ▼
   Dictionary              List (in memory)
```

### Integration Test Flow

```
Test Code
       │
       ▼
┌──────────────────┐
│ Lambda Handler   │ ← Real handler
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ TaskService      │ ← Real domain
└──────────────────┘
       │
       │ Real adapters
       ▼
┌──────────────────┐     ┌──────────────────┐
│ DynamoDB Adapter │     │ EventBridge      │
│ (Real AWS)       │     │ Adapter          │
└──────────────────┘     └──────────────────┘
       │                         │
       ▼                         ▼
┌──────────────────┐     ┌──────────────────┐
│ Test DynamoDB    │     │ Test EventBridge │
│ Table            │     │ Bus              │
└──────────────────┘     └──────────────────┘
```

## Benefits for Testing

### 1. Fast Unit Tests

**Without Hexagonal Architecture**:
```python
# ❌ Must mock boto3 for every test
@patch('boto3.resource')
@patch('boto3.client')
def test_create_task(mock_client, mock_resource):
    # Complex mock setup
    mock_table = Mock()
    mock_resource.return_value.Table.return_value = mock_table
    # ... more mock setup
    
    # Test
    result = lambda_handler(event, context)
    
    # Verify mocks were called correctly
    mock_table.put_item.assert_called_once_with(...)
```

**With Hexagonal Architecture**:
```python
# ✅ Simple fake injection
def test_create_task():
    # Simple setup
    repository = InMemoryTaskRepository()
    publisher = InMemoryEventPublisher()
    service = TaskService(repository, publisher)
    
    # Test
    task = service.create_task(title="Test Task")
    
    # Simple assertions
    assert task.title == "Test Task"
    assert repository.count() == 1
    assert publisher.count() == 1
```

### 2. Realistic Integration Tests

```python
# ✅ Test against real AWS
def test_create_task_integration():
    # Real DynamoDB adapter
    repository = DynamoDBTaskRepository(table_name="test-table")
    
    # Real AWS SDK calls
    task = repository.create_task(Task(title="Test"))
    
    # Verify in real DynamoDB
    response = boto3.client('dynamodb').get_item(
        TableName="test-table",
        Key={'task_id': {'S': task.task_id}}
    )
    assert response['Item']['title']['S'] == "Test"
```

### 3. Error Simulation

```python
# ✅ Simulate AWS errors without AWS
class ErrorSimulatingRepository:
    """Fake that simulates DynamoDB errors."""
    
    def create_task(self, task: Task) -> Task:
        # Simulate throttling
        raise ClientError(
            {'Error': {'Code': 'ProvisionedThroughputExceededException'}},
            'PutItem'
        )

def test_handles_throttling():
    repository = ErrorSimulatingRepository()
    service = TaskService(repository)
    
    with pytest.raises(RepositoryError):
        service.create_task(title="Test")
```

### 4. Layer-Specific Testing

Each layer can be tested independently:

- **Handler Layer**: Test HTTP parsing and response formatting
- **Domain Layer**: Test business logic in isolation
- **Integration Layer**: Test AWS SDK operations

## Implementation Patterns

### Self-Initializing Services

Services initialize their own dependencies but allow injection for testing:

```python
class TaskService:
    def __init__(
        self,
        repository: Optional[TaskRepositoryProtocol] = None,
        event_publisher: Optional[EventPublisherProtocol] = None
    ):
        """Initialize with optional dependency injection."""
        # Production: Use real implementations
        if repository is None:
            from shared.integration.dynamodb_adapter import DynamoDBTaskRepository
            repository = DynamoDBTaskRepository()
        
        if event_publisher is None:
            from shared.integration.eventbridge_adapter import EventBridgePublisher
            event_publisher = EventBridgePublisher()
        
        self.repository = repository
        self.event_publisher = event_publisher
```

**Benefits**:
- ✅ Works in production without configuration
- ✅ Easy to inject fakes for testing
- ✅ No dependency injection container needed

### Protocol-Based Interfaces

Use Python protocols instead of abstract base classes:

```python
from typing import Protocol

class TaskRepositoryProtocol(Protocol):
    """Protocol defines the contract."""
    def create_task(self, task: Task) -> Task: ...
```

**Benefits**:
- ✅ Structural typing (duck typing with type safety)
- ✅ No inheritance required
- ✅ IDE autocomplete and type checking
- ✅ Easy to create multiple implementations

### In-Memory Fakes

Create realistic fakes with in-memory storage:

```python
class InMemoryTaskRepository:
    """Fake repository with realistic behavior."""
    
    def __init__(self):
        self._tasks: Dict[str, Task] = {}
    
    def create_task(self, task: Task) -> Task:
        if task.task_id in self._tasks:
            raise ValueError("Task already exists")
        self._tasks[task.task_id] = task
        return task
    
    # Helper methods for testing
    def count(self) -> int:
        return len(self._tasks)
    
    def clear(self) -> None:
        self._tasks.clear()
```

**Benefits**:
- ✅ Realistic behavior (not just mocks)
- ✅ Fast execution (in-memory)
- ✅ Easy to debug
- ✅ Helper methods for test assertions

## Comparison: Before vs After

| Aspect | Before (Monolithic) | After (Hexagonal) |
|--------|---------------------|-------------------|
| **Testability** | Hard - requires extensive mocking | Easy - inject fakes |
| **Test Speed** | Slow - mock setup overhead | Fast - in-memory operations |
| **Maintainability** | Poor - changes ripple across layers | Good - isolated changes |
| **Flexibility** | Low - tightly coupled to AWS | High - swap implementations |
| **Clarity** | Low - mixed concerns | High - clear separation |
| **AWS Changes** | Breaks business logic tests | Only affects integration layer |
| **Business Logic** | Mixed with infrastructure | Pure and isolated |
| **Test Confidence** | Low - mocks don't match reality | High - real AWS tests |

## Lambda Packaging Benefits

### Before: Monolithic Packaging

```
task_handler.zip (100%)
├── task_api/
│   ├── handlers/
│   │   ├── task_handler.py          ✓ Used
│   │   └── notification_handler.py  ✗ Not used
│   ├── domain/
│   │   ├── task_service.py          ✓ Used
│   │   └── notification_service.py  ✗ Not used
│   ├── models/                      ✓ Used
│   └── integration/                 ✓ Used
└── dependencies/                    ✓ Used

notification_handler.zip (100%)
├── task_api/
│   ├── handlers/
│   │   ├── task_handler.py          ✗ Not used
│   │   └── notification_handler.py  ✓ Used
│   ├── domain/
│   │   ├── task_service.py          ✗ Not used
│   │   └── notification_service.py  ✓ Used
│   ├── models/                      ✗ Not used (mostly)
│   └── integration/                 ✓ Used
└── dependencies/                    ✓ Used
```

### After: Service-Based Packaging

```
task_service.zip (~70% of before)
├── services/
│   └── task_service/               ✓ All used
│       ├── handler.py
│       ├── domain/
│       └── models/
├── shared/
│   └── integration/                ✓ All used
└── dependencies/                   ✓ All used

notification_service.zip (~60% of before)
├── services/
│   └── notification_service/       ✓ All used
│       ├── handler.py
│       └── domain/
├── shared/
│   └── integration/                ✓ All used
└── dependencies/                   ✓ All used
```

### Packaging Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Task Service Package** | 100% | ~70% | 30% reduction |
| **Notification Service Package** | 100% | ~60% | 40% reduction |
| **Unused Code in Package** | 30-40% | 0% | Eliminated |
| **Cold Start Time** | Baseline | Faster | Smaller package |
| **Deployment Speed** | Baseline | Faster | Smaller upload |

### How CDK Bundles Services

```python
# infrastructure/core/task_api_stack.py

# Task Service Lambda
task_handler = PythonFunction(
    self, "TaskHandler",
    entry="services/task_service",  # Entry point
    index="handler.py",              # Handler file
    handler="lambda_handler",        # Handler function
    # CDK automatically:
    # 1. Starts from services/task_service/
    # 2. Follows imports to include:
    #    - services/task_service/domain/
    #    - services/task_service/models/
    #    - shared/integration/ (via imports)
    # 3. Excludes services/notification_service/ (not imported)
)

# Notification Service Lambda
notification_handler = PythonFunction(
    self, "NotificationHandler",
    entry="services/notification_service",  # Entry point
    index="handler.py",                     # Handler file
    handler="lambda_handler",               # Handler function
    # CDK automatically:
    # 1. Starts from services/notification_service/
    # 2. Follows imports to include:
    #    - services/notification_service/domain/
    #    - shared/integration/ (via imports)
    # 3. Excludes services/task_service/ (not imported)
)
```

## Next Steps

- **[Testing Guide](testing-guide.md)** - Learn how to test each layer
- **[Deployment Guide](deployment.md)** - Deploy the application
- **[Configuration Guide](configuration.md)** - Configure infrastructure

## References

- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/) by Alistair Cockburn
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) by Robert C. Martin
- [Ports and Adapters Pattern](https://herbertograca.com/2017/09/14/ports-adapters-architecture/)
- [Domain-Driven Design](https://martinfowler.com/bliki/BoundedContext.html) - Bounded Contexts by Martin Fowler
