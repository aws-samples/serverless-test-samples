"""
Centralized configuration for infrastructure resource naming.

Provides consistent naming patterns for all AWS resources with support
for environment-specific overrides via CDK context.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from constructs import Node


@dataclass
class InfrastructureConfig:
    """
    Configuration for infrastructure resource naming.

    Provides type-safe, computed resource names with support for
    environment-specific overrides via CDK context.

    Attributes:
        project_name: Base name for all resources (default: cns427-task-api)
        environment: Environment identifier (default: dev)
        region: AWS region for deployment (default: us-west-2)
    """

    project_name: str = 'cns427-task-api'
    environment: str = 'dev'
    region: str = 'us-west-2'

    # Core Infrastructure Resource Names

    def tasks_table_name(self) -> str:
        """
        Get DynamoDB table name for tasks.

        Returns:
            Table name in format: {project_name}-tasks
        """
        return f'{self.project_name}-tasks'

    def event_bus_name(self) -> str:
        """
        Get EventBridge custom event bus name.

        Returns:
            Event bus name in format: {project_name}-core-task-events
        """
        return f'{self.project_name}-core-task-events'

    def task_handler_function_name(self) -> str:
        """
        Get Lambda function name for task CRUD operations.

        Returns:
            Function name in format: {project_name}-task-handler
        """
        return f'{self.project_name}-task-handler'

    def notification_handler_function_name(self) -> str:
        """
        Get Lambda function name for notification processing.

        Returns:
            Function name in format: {project_name}-notification-handler
        """
        return f'{self.project_name}-notification-handler'

    def api_name(self) -> str:
        """
        Get API Gateway REST API name.

        Returns:
            API name in format: {project_name}-api
        """
        return f'{self.project_name}-api'

    def task_event_rule_name(self) -> str:
        """
        Get EventBridge rule name for task events.

        Returns:
            Rule name in format: {project_name}-task-event-rule
        """
        return f'{self.project_name}-task-event-rule'

    def log_group_name(self) -> str:
        """
        Get CloudWatch log group name.

        Returns:
            Log group name in format: /aws/lambda/{project_name}
        """
        return f'/aws/lambda/{self.project_name}'

    # Test Harness Infrastructure Resource Names

    def test_results_table_name(self) -> str:
        """
        Get DynamoDB table name for test results.

        Returns:
            Table name in format: {project_name}-test-results
        """
        return f'{self.project_name}-test-results'

    def test_subscriber_function_name(self) -> str:
        """
        Get Lambda function name for test event subscriber.

        Returns:
            Function name in format: {project_name}-test-subscriber
        """
        return f'{self.project_name}-test-subscriber'

    def test_event_rule_name(self) -> str:
        """
        Get EventBridge rule name for test events.

        Returns:
            Rule name in format: {project_name}-test-rule
        """
        return f'{self.project_name}-test-rule'

    def test_dlq_name(self) -> str:
        """
        Get SQS queue name for test event DLQ.

        Returns:
            Queue name in format: {project_name}-test-events-dlq
        """
        return f'{self.project_name}-test-events-dlq'

    def test_execution_role_name(self) -> str:
        """
        Get IAM role name for test execution.

        Returns:
            Role name in format: {project_name}-test-execution-role
        """
        return f'{self.project_name}-test-execution-role'

    def test_dashboard_name(self) -> str:
        """
        Get CloudWatch dashboard name for test monitoring.

        Returns:
            Dashboard name in format: {project_name}-test-monitoring
        """
        return f'{self.project_name}-test-monitoring'

    def test_harness_stack_name(self) -> str:
        """
        Get CloudFormation stack name for test harness infrastructure.

        Returns:
            Stack name in format: {project_name}-test-harness
        """
        return f'{self.project_name}-test-harness'

    # Monitoring Infrastructure Resource Names

    def dashboard_name(self) -> str:
        """
        Get CloudWatch dashboard name for main application.

        Returns:
            Dashboard name in format: {project_name}-dashboard
        """
        return f'{self.project_name}-dashboard'

    @classmethod
    def from_cdk_context(cls, node: 'Node') -> 'InfrastructureConfig':
        """
        Create configuration from CDK context.

        Loads configuration from cdk.json context or uses defaults.
        Supports CLI overrides via -c flag.

        Args:
            node: CDK construct node with context access

        Returns:
            InfrastructureConfig instance with values from context or defaults

        Example:
            >>> config = InfrastructureConfig.from_cdk_context(self.node)
            >>> table_name = config.tasks_table_name()
        """
        return cls(
            project_name=node.try_get_context('project_name') or cls.project_name,
            environment=node.try_get_context('environment') or cls.environment,
            region=node.try_get_context('region') or cls.region,
        )
