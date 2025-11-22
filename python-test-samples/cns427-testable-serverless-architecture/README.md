# CNS427 Task Management API

> **Companion code for AWS re:Invent 2025 talk CNS427:**  
> *"Supercharge Serverless Testing: Accelerate Development with Kiro"*

A serverless Task Management API demonstrating best practices for building testable, maintainable serverless applications using hexagonal architecture and comprehensive testing strategies.

## 🎯 What this project demonstrates

This codebase showcases how to build serverless applications that are:
- **Easy to test** at multiple levels (unit, integration, end-to-end)
- **Maintainable** through clean architecture and separation of concerns
- **Production-ready** with proper error handling and observability
- **AI-friendly** designed using AI-Driven Development Lifecycle (AI-DLC) methodology

## 📐 Architecture: Hexagonal design for testability

### The problem with traditional serverless code

```
❌ BEFORE: Monolithic Lambda (Hard to Test)
┌─────────────────────────────────────────┐
│  lambda_handler()                       │
│  ├─ HTTP parsing                        │
│  ├─ Business logic                      │
│  ├─ DynamoDB calls                      │
│  ├─ EventBridge calls                   │
│  └─ HTTP response                       │
└─────────────────────────────────────────┘

Problems:
• Everything mixed together
• Can't test without AWS
• Complex test setup
• Slow test execution
```

### Solution: Monorepo service pattern + Hexagonal architecture

```
✅ AFTER: Service-Based Architecture (Easy to Test, Optimized Packaging)

┌─────────────────────────────────────────────────────────────┐
│  TASK SERVICE (Complete Hexagon)                            │
│                                                             │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Handler (handler.py)                              │     │
│  │  • HTTP parsing only                               │     │
│  │  • Delegates to domain                             │     │
│  └────────────────────────────────────────────────────┘     │
│                        │                                    │
│                        ▼                                    │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Domain (domain/)                                  │     │
│  │  • Pure business logic                             │     │
│  │  • No AWS dependencies                             │     │
│  │  • Uses protocol interfaces                        │     │
│  └────────────────────────────────────────────────────┘     │
│                        │                                    │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Models (models/)                                  │     │
│  │  • Task domain models                              │     │
│  │  • API contracts                                   │     │
│  └────────────────────────────────────────────────────┘     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ Uses shared adapters
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  SHARED INFRASTRUCTURE                                      │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Integration (shared/integration/)                 │     │
│  │  • DynamoDB adapter                                │     │
│  │  • EventBridge adapter                             │     │
│  │  • Protocol interfaces                             │     │
│  └────────────────────────────────────────────────────┘     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ Uses shared adapters
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  NOTIFICATION SERVICE (Complete Hexagon)                    │
│                                                             │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Handler (handler.py)                              │     │
│  │  • Event parsing                                   │     │
│  │  • Delegates to domain                             │     │
│  └────────────────────────────────────────────────────┘     │
│                        │                                    │
│                        ▼                                    │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Domain (domain/)                                  │     │
│  │  • Event processing logic                          │     │
│  │  • No AWS dependencies                             │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘

Benefits:
✓ Each service is independent
✓ Optimized Lambda packages (30-40% smaller)
✓ Test without AWS (unit tests)
✓ Clear service boundaries
✓ Fast execution (milliseconds)
```

## 🧪 Testing strategy: The honeycomb model

Unlike traditional applications, serverless apps benefit from an **inverted testing pyramid** - the "honeycomb" model:

```
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

### Why honeycomb for serverless?

**Traditional Pyramid** (unit-heavy) doesn't work well for serverless because:
- Most bugs occur at service boundaries (DynamoDB, EventBridge, API Gateway)
- AWS SDK behavior is complex and hard to mock accurately
- Integration issues are the primary source of production failures

**Honeycomb Model** (integration-heavy) is better because:
- ✅ Tests real AWS service behavior
- ✅ Catches integration bugs early
- ✅ Validates error handling and retries
- ✅ Tests at the right level of abstraction

### Test distribution

```
Integration Tests:
├─ DynamoDB: Real AWS + error fakes
├─ EventBridge: Real AWS with test harness
└─ API Gateway: Real Lambda handler

Unit Tests:
├─ Domain logic: Pure business rules
├─ Handler: HTTP contracts
└─ Models: Validation logic

E2E Tests:
└─ Critical user workflows
```

## 🏗️ How This Codebase Implements Best Practices

### 1. **Dependency injection for testability**

```python
# services/task_service/domain/task_service.py
from shared.integration.interfaces import (
    TaskRepositoryProtocol,
    EventPublisherProtocol
)

class TaskService:
    def __init__(
        self,
        repository: TaskRepositoryProtocol,
        event_publisher: EventPublisherProtocol
    ):
        self.repository = repository
        self.event_publisher = event_publisher
```

**Benefits:**
- Inject real AWS adapters in production
- Inject in-memory fakes for unit tests
- Inject error-simulating fakes for error testing

### 2. **Protocol-based interfaces**

```python
# shared/integration/interfaces.py
from typing import Protocol
from services.task_service.models.task import Task

class TaskRepositoryProtocol(Protocol):
    def create_task(self, task: Task) -> Task: ...
    def get_task(self, task_id: str) -> Optional[Task]: ...
    def update_task(self, task: Task) -> Task: ...
    def delete_task(self, task_id: str) -> None: ...
```

**Benefits:**
- Swap implementations without changing domain code
- Multiple implementations (real, fake, mock)
- Type-safe with IDE support

### 3. **In-Memory fakes over mocks**

```python
# tests/shared/fakes/in_memory_repository.py
from services.task_service.models.task import Task

class InMemoryTaskRepository:
    def __init__(self):
        self._tasks: Dict[str, Task] = {}
    
    def create_task(self, task: Task) -> Task:
        self._tasks[task.task_id] = task
        return task
```

**Benefits:**
- Realistic behavior without AWS
- No complex mock setup
- Easy to debug
- Fast execution

### 4. **Real AWS integration tests**

```python
# tests/integration/test_dynamodb_integration.py
from shared.integration.dynamodb_adapter import DynamoDBTaskRepository
from services.task_service.models.task import Task

def test_create_task_persists_to_dynamodb():
    # Uses real DynamoDB table
    repository = DynamoDBTaskRepository(table_name="test-table")
    
    # Real AWS SDK calls
    task = repository.create_task(Task(title="Test"))
    
    # Verify in DynamoDB
    response = dynamodb.get_item(Key={"task_id": task.task_id})
    assert response["Item"]["title"] == "Test"
```

**Benefits:**
- Tests real AWS behavior
- Catches SDK quirks
- Validates IAM permissions
- Tests error handling

### 5. **EventBridge test harness**

```python
# Test harness captures events for verification
┌──────────────┐    ┌─────────────────┐    ┌──────────────┐
│ Lambda       │───▶│ EventBridge     │───▶│ Test Lambda  │
│ (publishes)  │    │ (TEST-* events) │    │ (captures)   │
└──────────────┘    └─────────────────┘    └──────────────┘
                                                    │
                                                    ▼
                                           ┌──────────────┐
                                           │ DynamoDB     │
                                           │ (test data)  │
                                           └──────────────┘
```

**Benefits:**
- Tests real EventBridge publishing
- Verifies event content and timing
- No production side effects
- Isolated test environment

## 🤖 AI-Driven development lifecycle (AI-DLC)

This codebase was developed using the **AI-DLC methodology** - a structured approach to using AI for software development that follows the software development lifecycle phases.

### AI-DLC phases

```
┌──────────────────────────────────────────────────────┐
│         INCEPTION PHASE                              │
│         Requirements & Architecture                  │
│                                                      │
│  🤖 AI validates architecture decisions              │
│  ✅ Layer separation                                 │
│  ✅ Pure business logic                              │
│   → Ready for Construction                           │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│         CONSTRUCTION PHASE                           │
│         Implementation & Testing                     │
│                                                      │
│  🤖 AI validates testing strategy                    │
│  ✅ 62% unit, 35% integration, 3% E2E (honeycomb)    │
│  ✅ Layer-appropriate testing                        │
│   → Ready for Operation                              │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│         OPERATION PHASE                              │
│         Deploy, Monitor, Optimize                    │
│                                                      │
│  🤖 AI analyzes production bugs                      │
│  🔥 75% bugs in integration layer                    │
│  🎯 Prioritized roadmap                              │
│  📈 Measurable targets                               │
└──────────────────────────────────────────────────────┘
```

### Learn more about AI-DLC

- 📄 **[AI-DLC whitepaper](https://prod.d13rzhkk8cj2z0.amplifyapp.com/)** - Comprehensive guide to the methodology
- 📊 **[Visual flow guide](docs/visual-flow-guide.md)** - Diagrams showing AI-DLC phases
- 📝 **[AI-DLC implementation guide](docs/ai-dlc.md)** - How we applied AI-DLC to this project

## 📚 Documentation

### Getting started
- **[Deployment guide](docs/deployment.md)** - Setup, deployment, and operations
- **[Configuration guide](docs/configuration.md)** - Infrastructure configuration and overrides

### Architecture & design
- **[Architecture guide](docs/architecture.md)** - Hexagonal architecture deep dive
- **[Testing guide](docs/testing-guide.md)** - Comprehensive testing strategies

### Methodology
- **[AI-DLC implementation guide](docs/ai-dlc.md)** - How we applied AI-DLC to this project

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Poetry
- Node.js 18+ (for AWS CDK)
- AWS CLI v2
- Docker (or alternatives like [Finch](https://github.com/runfinch))

### AWS configuration

**Configure AWS credentials and region before running any commands:**

```bash
# Configure AWS credentials and default region
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-west-2
```

All commands (deployment, testing, infrastructure management) will use these credentials and region. For detailed configuration options, see the **[Deployment Guide](docs/deployment.md)**.

### Installation

```bash
# Install dependencies
poetry install

# Verify setup
poetry run validate-setup
```

### Run unit tests (no AWS required)

```bash
# Fast, isolated tests
make test-unit

# Runs in milliseconds
# Tests pure business logic
# Uses in-memory fakes
```

### Deploy and run integration tests

```bash
# 1. Deploy main application
make deploy

# 2. Deploy test infrastructure
make deploy-test-infra

# 3. Verify test infrastructure
make check-test-infra

# 4. Run integration tests (requires AWS)
make test-integration

# 5. Run end to end tests (requires AWS)
make test-e2e
```

## 🎓 Key takeaways

### For Serverless developers

1. **Architecture**: Hexagonal architecture makes serverless apps testable
2. **Honeycomb > Pyramid**: Focus on integration tests for serverless
3. **Real AWS tests**: Test against real services, not just mocks
4. **Fast unit tests**: Use in-memory fakes for business logic
5. **Test harness**: Build infrastructure to support testing async integration

### For AI-Assisted development

1. **Structured approach**: AI-DLC provides a framework for AI collaboration
2. **Validation at each phase**: AI validates architecture, testing, and operations
3. **Measurable outcomes**: Track metrics at each phase
4. **Continuous improvement**: Feedback loops inform next iteration

## 📊 Project structure

This project uses a **monorepo service pattern** where each service is a complete hexagon with its own domain, models, and handler. Only infrastructure adapters are shared.

```
cns427-task-api/
├── services/                   # Microservices (hexagonal architecture)
│   ├── task_service/          # Task management service
│   │   ├── handler.py         # Lambda entry point
│   │   ├── domain/            # Business logic
│   │   │   ├── task_service.py
│   │   │   ├── business_rules.py
│   │   │   └── exceptions.py
│   │   ├── models/            # Domain models
│   │   │   ├── task.py
│   │   │   └── api.py
│   │   └── requirements.txt   # Service dependencies
│   └── notification_service/  # Event processing service
│       ├── handler.py         # Lambda entry point
│       ├── domain/            # Business logic
│       │   └── notification_service.py
│       └── requirements.txt   # Service dependencies
├── shared/                    # Shared infrastructure code
│   └── integration/           # AWS adapters (reusable)
│       ├── dynamodb_adapter.py
│       ├── eventbridge_adapter.py
│       └── interfaces.py
├── tests/                     # Test suites
│   ├── unit/                  # Unit tests (fast, isolated)
│   ├── integration/           # Integration tests (real AWS)
│   ├── property_based/        # Property-based tests (Hypothesis)
│   ├── e2e/                   # End-to-end tests
│   └── shared/                # Test utilities and fakes
├── infrastructure/            # CDK infrastructure code
│   ├── core/                  # Main application stacks
│   ├── test_harness/          # Test infrastructure
│   └── config.py              # Centralized configuration
└── docs/                      # Documentation
    ├── architecture.md        # Architecture deep dive
    ├── testing-guide.md       # Testing strategies
    ├── deployment.md          # Deployment guide
    ├── configuration.md       # Configuration guide
    ├── ai-dlc.md              # AI-DLC methodology
    ├── visual-flow-guide.md   # Visual flow diagrams
    └── cdk-nag-guide.md       # CDK validation guide
```

### Service-Oriented organization

**Why services?**
- Each service is a complete, independent hexagon
- Clear bounded contexts and responsibilities
- Optimized Lambda packaging (30-40% smaller)
- Independent deployment and scaling

**Task service** owns:
- Task CRUD operations
- Business rules and validation
- Task domain models
- API contracts

**Notification service** owns:
- Event processing
- Notification routing
- Event-specific logic

**Shared infrastructure** provides:
- Reusable AWS adapters
- Protocol interfaces
- Common utilities

For more details, see the **[Architecture Guide](docs/architecture.md)**.

## 🤝 Contributing

This is a demonstration project for the re:Invent talk. Feel free to use it as a reference for your own serverless applications!

## 📄 License

MIT-0 - See LICENSE file for details.

## 🔗 Resources

- **AWS re:Invent 2025 Session CNS427**: [Session Details](#)
- **AI-DLC Whitepaper**: [aws.amazon.com/ai-dlc](#)
- **AWS Lambda Best Practices**: [docs.aws.amazon.com/lambda](https://docs.aws.amazon.com/lambda)
- **Hexagonal Architecture**: [alistair.cockburn.us/hexagonal-architecture](https://alistair.cockburn.us/hexagonal-architecture/)

---

**Built with ❤️ using AI-Driven Development Lifecycle (AI-DLC)**
