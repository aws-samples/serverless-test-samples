# Configuration Guide

This guide explains the centralized configuration system used for infrastructure resource naming and how to customize it for different environments.

## Table of Contents

- [Overview](#overview)
- [Configuration Module](#configuration-module)
- [Default Configuration](#default-configuration)
- [Using Configuration in Stacks](#using-configuration-in-stacks)
- [Overriding Configuration](#overriding-configuration)
- [Available Configuration Methods](#available-configuration-methods)
- [Best Practices](#best-practices)

## Overview

The project uses a centralized configuration module (`infrastructure/config.py`) for all resource naming. This provides:

- **Consistent naming patterns** across all resources
- **Type-safe configuration** with IDE autocomplete
- **Environment-specific overrides** via CDK context
- **Easy multi-environment deployments**
- **Single source of truth** for resource names

## Configuration Module

### Location

`infrastructure/config.py`

### Key Features

1. **Dataclass-based**: Uses Python dataclasses for type safety
2. **Computed names**: Resource names are computed from base configuration
3. **CDK context integration**: Loads values from `cdk.json` or CLI overrides
4. **Protocol-based**: Provides methods for each resource type

### Basic Structure

```python
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from constructs import Node

@dataclass
class InfrastructureConfig:
    """Configuration for infrastructure resource naming."""
    
    project_name: str = "cns427-task-api"
    environment: str = "dev"
    region: str = "us-west-2"
    
    def tasks_table_name(self) -> str:
        """Get DynamoDB table name for tasks."""
        return f"{self.project_name}-tasks"
    
    # ... more methods
    
    @classmethod
    def from_cdk_context(cls, node: 'Node') -> 'InfrastructureConfig':
        """Create configuration from CDK context."""
        return cls(
            project_name=node.try_get_context('project_name') or cls.project_name,
            environment=node.try_get_context('environment') or cls.environment,
            region=node.try_get_context('region') or cls.region,
        )
```

## Default Configuration

Default values are defined in `cdk.json`:

```json
{
  "app": "python app.py",
  "context": {
    "project_name": "cns427-task-api",
    "environment": "dev",
    "region": "us-west-2"
  }
}
```

### Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `project_name` | `cns427-task-api` | Base name for all resources |
| `environment` | `dev` | Environment identifier (dev, staging, prod) |
| `region` | `us-west-2` | AWS region for deployment |

## Using Configuration in Stacks

### Loading Configuration

In every CDK stack, load the configuration from context:

```python
from infrastructure.config import InfrastructureConfig

class MyStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Load configuration from CDK context
        config = InfrastructureConfig.from_cdk_context(self.node)
```

### Example 1: Core Stack (TaskApiCoreStack)

```python
from infrastructure.config import InfrastructureConfig

class TaskApiCoreStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Load configuration from CDK context
        config = InfrastructureConfig.from_cdk_context(self.node)

        # DynamoDB table with configured name
        self.tasks_table = dynamodb.Table(
            self,
            'TasksTable',
            table_name=config.tasks_table_name(),  # Returns: cns427-task-api-tasks
            partition_key=dynamodb.Attribute(name='task_id', type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            # ...
        )

        # EventBridge custom event bus with configured name
        self.event_bus = events.EventBus(
            self, 
            'TaskEventBus', 
            event_bus_name=config.event_bus_name()  # Returns: cns427-task-api-core-task-events
        )

        # CloudWatch log group with configured name
        self.app_log_group = logs.LogGroup(
            self,
            'AppLogGroup',
            log_group_name=config.log_group_name(),  # Returns: /aws/lambda/cns427-task-api
            retention=logs.RetentionDays.ONE_WEEK,
        )
```

### Example 2: API Stack (TaskApiStack)

```python
class TaskApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, core_stack: TaskApiCoreStack, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Load configuration
        config = InfrastructureConfig.from_cdk_context(self.node)

        # Lambda function with configured name
        self.task_handler = PythonFunction(
            self,
            'TaskHandler',
            function_name=config.task_handler_function_name(),  # Returns: cns427-task-api-task-handler
            entry='task_api/handlers',
            # ...
        )

        # API Gateway with configured name
        self.api = apigateway.RestApi(
            self,
            'TaskApi',
            rest_api_name=config.api_name(),  # Returns: cns427-task-api-api
            description='CNS427 Task Management API',
        )

        # EventBridge rule with configured name
        task_event_rule = events.Rule(
            self,
            'TaskEventRule',
            rule_name=config.task_event_rule_name(),  # Returns: cns427-task-api-task-event-rule
            event_bus=self.event_bus,
        )
```

### Example 3: Test Harness Stack (TestInfrastructureStack)

```python
class TestInfrastructureStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Load configuration
        config = InfrastructureConfig.from_cdk_context(self.node)

        # Test results table with configured name
        self.test_results_table = dynamodb.Table(
            self, 
            "TestResultsTable",
            table_name=config.test_results_table_name(),  # Returns: cns427-task-api-test-results
            # ...
        )

        # Test subscriber Lambda with configured name
        self.test_subscriber_lambda = lambda_.Function(
            self,
            'TestHarnessLambda',
            function_name=config.test_subscriber_function_name(),  # Returns: cns427-task-api-test-subscriber
            # ...
        )

        # Test event rule with configured name
        self.test_event_rule = events.Rule(
            self, 
            "TestEventRule",
            rule_name=config.test_event_rule_name(),  # Returns: cns427-task-api-test-rule
            # ...
        )
```

## Overriding Configuration

### Method 1: Edit cdk.json

Update the context values in `cdk.json`:

```json
{
  "context": {
    "project_name": "my-custom-project",
    "environment": "prod",
    "region": "us-east-1"
  }
}
```

**When to use:**
- Permanent configuration changes
- Team-wide defaults
- Version-controlled settings

### Method 2: CLI Context Parameters

Override values at deployment time:

```bash
# Deploy to production
poetry run cdk deploy -c environment=prod -c project_name=my-app-prod

# Deploy to different region
poetry run cdk deploy -c region=eu-west-1

# Multiple overrides
poetry run cdk deploy -c environment=staging -c project_name=my-app-staging -c region=ap-southeast-1
```

**When to use:**
- One-time deployments
- Testing different configurations
- CI/CD pipelines with dynamic values
- Personal development environments

### Method 3: Environment Variables (for Application Code)

Application code can read configuration from environment variables:

```python
import os

# Lambda environment variables set by CDK
TASKS_TABLE_NAME = os.getenv('TASKS_TABLE_NAME')
EVENT_BUS_NAME = os.getenv('EVENT_BUS_NAME')
AWS_REGION = os.getenv('AWS_REGION')
```

## Available Configuration Methods

### Core Infrastructure

| Method | Returns | Example Output |
|--------|---------|----------------|
| `tasks_table_name()` | DynamoDB tasks table name | `cns427-task-api-tasks` |
| `event_bus_name()` | EventBridge custom event bus name | `cns427-task-api-core-task-events` |
| `task_handler_function_name()` | Task CRUD Lambda function name | `cns427-task-api-task-handler` |
| `notification_handler_function_name()` | Notification Lambda function name | `cns427-task-api-notification-handler` |
| `api_name()` | API Gateway REST API name | `cns427-task-api-api` |
| `task_event_rule_name()` | EventBridge rule name | `cns427-task-api-task-event-rule` |
| `log_group_name()` | CloudWatch log group name | `/aws/lambda/cns427-task-api` |
| `dashboard_name()` | CloudWatch dashboard name | `cns427-task-api-dashboard` |

### Test Harness Infrastructure

| Method | Returns | Example Output |
|--------|---------|----------------|
| `test_results_table_name()` | Test results DynamoDB table name | `cns427-task-api-test-results` |
| `test_subscriber_function_name()` | Test subscriber Lambda function name | `cns427-task-api-test-subscriber` |
| `test_event_rule_name()` | Test EventBridge rule name | `cns427-task-api-test-rule` |
| `test_dlq_name()` | Test dead-letter queue name | `cns427-task-api-test-events-dlq` |
| `test_execution_role_name()` | Test IAM role name | `cns427-task-api-test-execution-role` |
| `test_dashboard_name()` | Test monitoring dashboard name | `cns427-task-api-test-monitoring` |

## Best Practices

### 1. Always Use Configuration Methods

```python
# ✅ DO: Use configuration methods
table_name = config.tasks_table_name()

# ❌ DON'T: Hardcode resource names
table_name = "cns427-task-api-tasks"
```

### 2. Load Configuration Once Per Stack

```python
# ✅ DO: Load once in __init__
class MyStack(Stack):
    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        config = InfrastructureConfig.from_cdk_context(self.node)
        # Use config throughout the stack

# ❌ DON'T: Load multiple times
def create_table(self):
    config = InfrastructureConfig.from_cdk_context(self.node)  # Wasteful
```

### 3. Use Descriptive Project Names

```python
# ✅ DO: Use descriptive names
project_name = "my-company-task-api-prod"

# ❌ DON'T: Use generic names
project_name = "app"
```

### 4. Include Environment in Project Name for Production

```bash
# ✅ DO: Separate production resources
poetry run cdk deploy -c project_name=task-api-prod -c environment=prod

# ❌ DON'T: Use same name for all environments
poetry run cdk deploy -c project_name=task-api
```

### 5. Document Custom Configurations

If you add custom configuration methods, document them:

```python
def custom_resource_name(self) -> str:
    """
    Get custom resource name.
    
    Returns:
        Resource name in format: {project_name}-custom-resource
        
    Example:
        >>> config = InfrastructureConfig(project_name="my-app")
        >>> config.custom_resource_name()
        'my-app-custom-resource'
    """
    return f"{self.project_name}-custom-resource"
```

## Common Scenarios

### Scenario 1: Deploy to Multiple Environments

```bash
# Development
poetry run cdk deploy --all -c environment=dev

# Staging
poetry run cdk deploy --all \
  -c environment=staging \
  -c project_name=cns427-task-api-staging

# Production
poetry run cdk deploy --all \
  -c environment=prod \
  -c project_name=cns427-task-api-prod \
  -c region=us-east-1
```

### Scenario 2: Deploy to Multiple Regions

```bash
# US West
poetry run cdk deploy --all \
  -c region=us-west-2 \
  -c project_name=task-api-west

# EU West
poetry run cdk deploy --all \
  -c region=eu-west-1 \
  -c project_name=task-api-eu
```

### Scenario 3: Personal Development Environment

```bash
# Use your name in project name
poetry run cdk deploy --all \
  -c project_name=task-api-john-dev \
  -c environment=dev
```

### Scenario 4: CI/CD Pipeline

```bash
# Use environment variables in CI/CD
export PROJECT_NAME="task-api-${CI_ENVIRONMENT_NAME}"
export ENVIRONMENT="${CI_ENVIRONMENT_NAME}"
export REGION="${AWS_REGION}"

poetry run cdk deploy --all \
  -c project_name="${PROJECT_NAME}" \
  -c environment="${ENVIRONMENT}" \
  -c region="${REGION}"
```

## Troubleshooting

### Issue: Resources Not Found

**Problem:** Can't find deployed resources

**Solution:** Check that you're using the same configuration values:
```bash
# List stacks to see what's deployed
poetry run cdk list

# Check context values
cat cdk.json | grep -A 5 "context"
```

### Issue: Resource Name Conflicts

**Problem:** `Resource already exists` error

**Solution:** Use a different project name:
```bash
poetry run cdk deploy -c project_name=my-unique-name
```

### Issue: Configuration Not Applied

**Problem:** Changes to `cdk.json` not taking effect

**Solution:** Clear CDK cache and redeploy:
```bash
rm -rf cdk.out/
poetry run cdk deploy --all
```

## Next Steps

- **[Deployment Guide](deployment.md)** - Deploy with custom configuration
- **[Architecture Guide](architecture.md)** - Understand how configuration is used
- **[Testing Guide](testing-guide.md)** - Test with different configurations

## References

- [AWS CDK Context](https://docs.aws.amazon.com/cdk/v2/guide/context.html)
- [Python Dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [Infrastructure as Code Best Practices](https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-infrastructure-as-code/welcome.html)
