"""
Test Infrastructure Stack

CDK stack for EventBridge integration testing infrastructure including
test results table, test subscriber Lambda, and EventBridge rules.
"""

from aws_cdk import (
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack,
)
from aws_cdk import (
    aws_cloudwatch as cloudwatch,
)
from aws_cdk import (
    aws_dynamodb as dynamodb,
)
from aws_cdk import (
    aws_events as events,
)
from aws_cdk import (
    aws_events_targets as targets,
)
from aws_cdk import (
    aws_iam as iam,
)
from aws_cdk import (
    aws_lambda as lambda_,
)
from aws_cdk import (
    aws_logs as logs,
)
from aws_cdk import (
    aws_sqs as sqs,
)
from constructs import Construct

from infrastructure.config import InfrastructureConfig


class TestInfrastructureStack(Stack):
    """CDK Stack for EventBridge integration test infrastructure."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Load configuration
        config = InfrastructureConfig.from_cdk_context(self.node)

        # Test Results DynamoDB Table
        self.test_results_table = dynamodb.Table(
            self,
            'TestResultsTable',
            table_name=config.test_results_table_name(),
            partition_key=dynamodb.Attribute(name='test_run_id', type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name='event_timestamp', type=dynamodb.AttributeType.STRING),
            time_to_live_attribute='ttl',
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            point_in_time_recovery_specification=dynamodb.PointInTimeRecoverySpecification(
                point_in_time_recovery_enabled=False
            ),  # Not needed for test data
        )

        # CloudWatch Log Group for Test Subscriber Lambda
        test_subscriber_log_group = logs.LogGroup(
            self,
            'TestSubscriberLogGroup',
            log_group_name=f'/aws/lambda/{config.test_subscriber_function_name()}',
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Test Subscriber Lambda Function
        self.test_subscriber_lambda = lambda_.Function(
            self,
            'TestHarnessLambda',
            function_name=config.test_subscriber_function_name(),
            runtime=lambda_.Runtime.PYTHON_3_13,
            architecture=lambda_.Architecture.ARM_64,
            code=lambda_.Code.from_asset(
                '.', exclude=['*.md', 'cdk.out', '*.sh', 'app.py', 'cdk.json', 'test_infrastructure_stack.py', '__pycache__']
            ),
            handler='test_event_subscriber.handler',
            environment={'TEST_RESULTS_TABLE_NAME': self.test_results_table.table_name, 'LOG_LEVEL': 'INFO'},
            timeout=Duration.seconds(30),
            memory_size=256,
            log_group=test_subscriber_log_group,
            description='Captures EventBridge test events for integration testing',
        )

        # Grant Lambda permissions to write to test results table
        self.test_results_table.grant_write_data(self.test_subscriber_lambda)

        # Import the custom event bus
        custom_event_bus = events.EventBus.from_event_bus_name(self, 'CustomEventBus', config.event_bus_name())

        # EventBridge Rule for Test Events on Custom Bus
        self.test_event_rule = events.Rule(
            self,
            'TestEventRule',
            rule_name=config.test_event_rule_name(),
            description='Routes TEST-* events to test subscriber Lambda',
            event_bus=custom_event_bus,
            event_pattern=events.EventPattern(source=['TEST-cns427-task-api'], detail_type=events.Match.prefix('TEST-')),
            enabled=True,
        )

        # Add Lambda as target for the rule
        self.test_event_rule.add_target(targets.LambdaFunction(self.test_subscriber_lambda, retry_attempts=2, max_event_age=Duration.minutes(5)))

        # Grant EventBridge permission to invoke Lambda
        self.test_subscriber_lambda.add_permission(
            'AllowEventBridgeInvoke',
            principal=iam.ServicePrincipal('events.amazonaws.com'),
            action='lambda:InvokeFunction',
            source_arn=self.test_event_rule.rule_arn,
        )

        # Dead Letter Queue for failed test events
        self.test_dlq = sqs.Queue(
            self, 'TestEventDLQ', queue_name=config.test_dlq_name(), retention_period=Duration.days(7), visibility_timeout=Duration.seconds(300)
        )

        # IAM Role for integration tests
        self.test_execution_role = iam.Role(
            self,
            'TestExecutionRole',
            role_name=config.test_execution_role_name(),
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole')],
            inline_policies={
                'EventBridgeTestPolicy': iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=['events:PutEvents'],
                            resources=['*'],
                            conditions={'StringEquals': {'events:source': 'TEST-cns427-task-api'}},
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=['dynamodb:Query', 'dynamodb:GetItem', 'dynamodb:PutItem', 'dynamodb:DeleteItem'],
                            resources=[self.test_results_table.table_arn],
                        ),
                    ]
                )
            },
        )

        # CloudWatch Dashboard for test monitoring
        self.test_dashboard = cloudwatch.Dashboard(
            self,
            'TestDashboard',
            dashboard_name=config.test_dashboard_name(),
            widgets=[
                [
                    cloudwatch.GraphWidget(
                        title='Test Subscriber Lambda Metrics',
                        left=[
                            self.test_subscriber_lambda.metric_invocations(),
                            self.test_subscriber_lambda.metric_errors(),
                            self.test_subscriber_lambda.metric_duration(),
                        ],
                        width=12,
                        height=6,
                    )
                ],
                [
                    cloudwatch.GraphWidget(
                        title='Test Results Table Metrics',
                        left=[
                            self.test_results_table.metric_consumed_read_capacity_units(),
                            self.test_results_table.metric_consumed_write_capacity_units(),
                        ],
                        width=12,
                        height=6,
                    )
                ],
                [
                    cloudwatch.SingleValueWidget(
                        title='Test Events DLQ Messages', metrics=[self.test_dlq.metric_approximate_number_of_messages_visible()], width=6, height=3
                    ),
                    cloudwatch.SingleValueWidget(
                        title='EventBridge Rule Invocations',
                        metrics=[
                            cloudwatch.Metric(
                                namespace='AWS/Events',
                                metric_name='SuccessfulInvocations',
                                dimensions_map={'RuleName': self.test_event_rule.rule_name},
                            )
                        ],
                        width=6,
                        height=3,
                    ),
                ],
            ],
        )

        # Output important ARNs and names for test configuration
        CfnOutput(self, 'TestResultsTableName', value=self.test_results_table.table_name, description='DynamoDB table name for test results')

        CfnOutput(self, 'TestSubscriberLambdaArn', value=self.test_subscriber_lambda.function_arn, description='Test subscriber Lambda function ARN')

        CfnOutput(self, 'TestEventRuleArn', value=self.test_event_rule.rule_arn, description='EventBridge rule ARN for test events')

        CfnOutput(self, 'TestExecutionRoleArn', value=self.test_execution_role.role_arn, description='IAM role ARN for test execution')


# Helper function to create test infrastructure app
def create_test_infrastructure_app():
    """Create CDK app with test infrastructure stack."""
    from aws_cdk import App

    app = App()

    TestInfrastructureStack(
        app,
        'CNS427TaskApiTestInfrastructure',
        description='EventBridge integration test infrastructure for CNS427 Task API',
        env={'account': app.node.try_get_context('account'), 'region': app.node.try_get_context('region') or 'us-east-1'},
    )

    return app


if __name__ == '__main__':
    # For direct execution
    app = create_test_infrastructure_app()
    app.synth()
