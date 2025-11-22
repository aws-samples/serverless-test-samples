"""CDK stack for CNS427 Task Management API."""

from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
)
from aws_cdk import (
    aws_dynamodb as dynamodb,
)
from aws_cdk import (
    aws_events as events,
)
from aws_cdk import (
    aws_iam as iam,
)
from aws_cdk import (
    aws_logs as logs,
)
from cdk_nag import NagSuppressions
from constructs import Construct

from infrastructure.config import InfrastructureConfig


class TaskApiCoreStack(Stack):
    """Core infrastructure stack for Task API."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Load configuration
        config = InfrastructureConfig.from_cdk_context(self.node)

        # DynamoDB table for tasks
        self.tasks_table = dynamodb.Table(
            self,
            'TasksTable',
            table_name=config.tasks_table_name(),
            partition_key=dynamodb.Attribute(name='task_id', type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,  # For demo purposes
            point_in_time_recovery_specification=dynamodb.PointInTimeRecoverySpecification(point_in_time_recovery_enabled=True),
        )

        # EventBridge custom event bus
        self.event_bus = events.EventBus(self, 'TaskEventBus', event_bus_name=config.event_bus_name())

        # CloudWatch log group for application logs
        self.app_log_group = logs.LogGroup(
            self,
            'AppLogGroup',
            log_group_name=config.log_group_name(),
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # IAM role for Lambda functions
        # Using inline policies instead of AWS managed policies for better security (CDK Nag: AwsSolutions-IAM4)
        self.lambda_execution_role = iam.Role(
            self,
            'LambdaExecutionRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            description='Execution role for Task API Lambda functions',
        )

        # Add CloudWatch Logs permissions (inline policy instead of AWSLambdaBasicExecutionRole)
        # Scoped to specific log groups to avoid wildcards (CDK Nag: AwsSolutions-IAM5)
        self.lambda_execution_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    'logs:CreateLogGroup',
                    'logs:CreateLogStream',
                    'logs:PutLogEvents',
                ],
                resources=[
                    f'arn:aws:logs:{self.region}:{self.account}:log-group:/aws/lambda/{config.task_handler_function_name()}:*',
                    f'arn:aws:logs:{self.region}:{self.account}:log-group:/aws/lambda/{config.notification_handler_function_name()}:*',
                ],
            )
        )

        # Grant DynamoDB permissions
        self.tasks_table.grant_read_write_data(self.lambda_execution_role)

        # Grant EventBridge permissions
        self.event_bus.grant_put_events_to(self.lambda_execution_role)

        # Grant CloudWatch Logs permissions for application log group
        self.app_log_group.grant_write(self.lambda_execution_role)

        # Add X-Ray tracing permissions
        # Note: X-Ray requires wildcard resources as traces can be sent to any region
        self.lambda_execution_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=['xray:PutTraceSegments', 'xray:PutTelemetryRecords'],
                resources=['*'],  # X-Ray requires wildcard - this is acceptable
            )
        )

        # Suppress CDK Nag warnings for acceptable wildcards
        NagSuppressions.add_resource_suppressions(
            self.lambda_execution_role,
            [
                {
                    'id': 'AwsSolutions-IAM5',
                    'reason': 'X-Ray tracing requires wildcard permissions to send traces to any region. This is an AWS service requirement and is documented in AWS X-Ray documentation.',
                    'appliesTo': ['Resource::*'],
                },
                {
                    'id': 'AwsSolutions-IAM5',
                    'reason': 'CloudWatch Logs requires wildcard suffix (:*) to allow log stream creation within the log group. '
                    'The log group itself is scoped to specific Lambda functions. This is standard AWS practice for Lambda logging.',
                    'appliesTo': [
                        f'Resource::arn:aws:logs:{self.region}:<AWS::AccountId>:log-group:/aws/lambda/{config.task_handler_function_name()}:*',
                        f'Resource::arn:aws:logs:{self.region}:<AWS::AccountId>:log-group:/aws/lambda/{config.notification_handler_function_name()}:*',
                    ],
                },
            ],
            apply_to_children=True,
        )


class TaskApiStack(Stack):
    """API infrastructure stack for Task API."""

    def __init__(self, scope: Construct, construct_id: str, core_stack: TaskApiCoreStack, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Load configuration
        config = InfrastructureConfig.from_cdk_context(self.node)

        # Import core resources
        self.tasks_table = core_stack.tasks_table
        self.event_bus = core_stack.event_bus
        self.lambda_role = core_stack.lambda_execution_role

        # Lambda function for task CRUD operations
        from aws_cdk import BundlingOptions
        from aws_cdk import aws_lambda as lambda_

        # Create log group for task handler
        task_handler_log_group = logs.LogGroup(
            self,
            'TaskHandlerLogGroup',
            log_group_name=f'/aws/lambda/{config.task_handler_function_name()}',
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.task_handler = lambda_.Function(
            self,
            'TaskHandler',
            function_name=config.task_handler_function_name(),
            runtime=lambda_.Runtime.PYTHON_3_13,
            architecture=lambda_.Architecture.ARM_64,
            handler='services.task_service.handler.lambda_handler',
            code=lambda_.Code.from_asset(
                '.',
                bundling=BundlingOptions(
                    image=lambda_.Runtime.PYTHON_3_13.bundling_image,
                    platform='linux/arm64',
                    command=[
                        'bash',
                        '-c',
                        'pip install -r services/task_service/requirements.txt -t /asset-output && '
                        + 'cp -r services /asset-output/ && '
                        + 'cp -r shared /asset-output/',
                    ],
                ),
            ),
            role=self.lambda_role,
            timeout=Duration.seconds(30),
            memory_size=512,
            tracing=lambda_.Tracing.ACTIVE,
            log_group=task_handler_log_group,
            description='Handles task CRUD operations via API Gateway with DynamoDB persistence and EventBridge publishing',
            environment={
                'TASKS_TABLE_NAME': self.tasks_table.table_name,
                'EVENT_BUS_NAME': self.event_bus.event_bus_name,
                'POWERTOOLS_SERVICE_NAME': 'task-api',
                'POWERTOOLS_METRICS_NAMESPACE': 'CNS427/TaskAPI',
                'LOG_LEVEL': 'INFO',
            },
        )

        # Lambda function for notification processing
        # Create log group for notification handler
        notification_handler_log_group = logs.LogGroup(
            self,
            'NotificationHandlerLogGroup',
            log_group_name=f'/aws/lambda/{config.notification_handler_function_name()}',
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.notification_handler = lambda_.Function(
            self,
            'NotificationHandler',
            function_name=config.notification_handler_function_name(),
            runtime=lambda_.Runtime.PYTHON_3_13,
            architecture=lambda_.Architecture.ARM_64,
            handler='services.notification_service.handler.lambda_handler',
            code=lambda_.Code.from_asset(
                '.',
                bundling=BundlingOptions(
                    image=lambda_.Runtime.PYTHON_3_13.bundling_image,
                    platform='linux/arm64',
                    command=[
                        'bash',
                        '-c',
                        'pip install -r services/notification_service/requirements.txt -t /asset-output && '
                        + 'cp -r services /asset-output/ && '
                        + 'cp -r shared /asset-output/',
                    ],
                ),
            ),
            role=self.lambda_role,
            timeout=Duration.seconds(30),
            memory_size=256,
            tracing=lambda_.Tracing.ACTIVE,
            log_group=notification_handler_log_group,
            description='Processes task events from EventBridge and handles notification logic',
            environment={'POWERTOOLS_SERVICE_NAME': 'task-notifications', 'POWERTOOLS_METRICS_NAMESPACE': 'CNS427/TaskAPI', 'LOG_LEVEL': 'INFO'},
        )

        # API Gateway
        from aws_cdk import CfnOutput
        from aws_cdk import aws_apigateway as apigateway

        self.api = apigateway.RestApi(
            self,
            'TaskApi',
            rest_api_name=config.api_name(),
            description='CNS427 Task Management API',
            cloud_watch_role=False,  # Disable automatic role creation to avoid account-level conflicts
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=['Content-Type', 'Authorization', 'X-Amz-Date', 'X-Amz-Security-Token'],
            ),
        )

        # Add request validator for basic input validation (CDK Nag: AwsSolutions-APIG2)
        request_validator = self.api.add_request_validator(
            'RequestValidator',
            validate_request_body=True,
            validate_request_parameters=True,
        )

        # Lambda integration
        task_integration = apigateway.LambdaIntegration(self.task_handler, proxy=True)

        # API Gateway resources and methods with IAM authorization and request validation
        tasks_resource = self.api.root.add_resource('tasks')
        tasks_resource.add_method(
            'GET',
            task_integration,
            authorization_type=apigateway.AuthorizationType.IAM,
            request_validator=request_validator,
        )  # List tasks
        tasks_resource.add_method(
            'POST',
            task_integration,
            authorization_type=apigateway.AuthorizationType.IAM,
            request_validator=request_validator,
        )  # Create task

        task_resource = tasks_resource.add_resource('{id}')
        task_resource.add_method(
            'GET',
            task_integration,
            authorization_type=apigateway.AuthorizationType.IAM,
            request_validator=request_validator,
        )  # Get task
        task_resource.add_method(
            'PUT',
            task_integration,
            authorization_type=apigateway.AuthorizationType.IAM,
            request_validator=request_validator,
        )  # Update task
        task_resource.add_method(
            'DELETE',
            task_integration,
            authorization_type=apigateway.AuthorizationType.IAM,
            request_validator=request_validator,
        )  # Delete task

        # Output API endpoint for E2E tests
        CfnOutput(self, 'ApiEndpoint', value=self.api.url, description='API Gateway endpoint URL', export_name=f'{config.project_name}-api-endpoint')

        # EventBridge rule for task events
        task_event_rule = events.Rule(
            self,
            'TaskEventRule',
            rule_name=config.task_event_rule_name(),
            event_bus=self.event_bus,
            event_pattern=events.EventPattern(source=['cns427-task-api'], detail_type=['TaskCreated', 'TaskUpdated', 'TaskDeleted']),
        )

        # Add notification handler as target
        from aws_cdk import aws_events_targets as targets

        task_event_rule.add_target(targets.LambdaFunction(self.notification_handler))

        # CDK Nag Suppressions for API Gateway
        # These are acceptable for demo/educational purposes to reduce cost and complexity
        NagSuppressions.add_stack_suppressions(
            self,
            [
                {
                    'id': 'AwsSolutions-COG4',
                    'reason': 'Demo/Educational Code: Using IAM authentication instead of Cognito. '
                    'IAM auth with SigV4 signing is appropriate for this demonstration and provides '
                    'sufficient security without the added complexity and cost of Cognito user pools. '
                    'All API methods require valid AWS credentials.',
                },
                {
                    'id': 'AwsSolutions-APIG1',
                    'reason': 'Demo/Educational Code: API Gateway access logging disabled to reduce costs. '
                    'CloudWatch Logs from Lambda functions provide sufficient observability for demonstration purposes. '
                    'For production use, enable access logging with: deploy_options={"access_log_destination": ...}',
                },
                {
                    'id': 'AwsSolutions-APIG3',
                    'reason': 'Demo/Educational Code: AWS WAF not configured to reduce costs. '
                    'IAM authentication already restricts API access to authorized AWS principals only. '
                    'WAF would add significant cost (~$5-10/month minimum) without substantial benefit for a demo API. '
                    'For production use, consider adding WAF for additional protection against web exploits.',
                },
                {
                    'id': 'AwsSolutions-APIG6',
                    'reason': 'Demo/Educational Code: CloudWatch logging at API Gateway stage level disabled to reduce costs. '
                    'Lambda function logs (enabled) provide sufficient observability for demonstration purposes. '
                    'API Gateway stage logging would duplicate information already captured in Lambda logs. '
                    'For production use, enable stage logging for detailed API Gateway metrics.',
                },
            ],
        )


class TaskApiMonitoringStack(Stack):
    """Monitoring and observability stack for Task API."""

    def __init__(self, scope: Construct, construct_id: str, api_stack: TaskApiStack, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Load configuration
        config = InfrastructureConfig.from_cdk_context(self.node)

        # Import resources from API stack
        self.task_handler = api_stack.task_handler
        self.notification_handler = api_stack.notification_handler
        self.api = api_stack.api

        from aws_cdk import aws_cloudwatch as cloudwatch

        # CloudWatch Dashboard
        self.dashboard = cloudwatch.Dashboard(self, 'TaskApiDashboard', dashboard_name=config.dashboard_name())

        # Lambda metrics
        task_handler_errors = cloudwatch.Metric(
            namespace='AWS/Lambda', metric_name='Errors', dimensions_map={'FunctionName': self.task_handler.function_name}, statistic='Sum'
        )

        task_handler_duration = cloudwatch.Metric(
            namespace='AWS/Lambda', metric_name='Duration', dimensions_map={'FunctionName': self.task_handler.function_name}, statistic='Average'
        )

        # API Gateway metrics
        api_4xx_errors = cloudwatch.Metric(
            namespace='AWS/ApiGateway', metric_name='4XXError', dimensions_map={'ApiName': self.api.rest_api_name}, statistic='Sum'
        )

        api_5xx_errors = cloudwatch.Metric(
            namespace='AWS/ApiGateway', metric_name='5XXError', dimensions_map={'ApiName': self.api.rest_api_name}, statistic='Sum'
        )

        # Add widgets to dashboard
        self.dashboard.add_widgets(
            cloudwatch.GraphWidget(title='Lambda Errors', left=[task_handler_errors], width=12, height=6),
            cloudwatch.GraphWidget(title='Lambda Duration', left=[task_handler_duration], width=12, height=6),
            cloudwatch.GraphWidget(title='API Gateway Errors', left=[api_4xx_errors, api_5xx_errors], width=24, height=6),
        )

        # CloudWatch Alarms
        cloudwatch.Alarm(
            self,
            'TaskHandlerErrorAlarm',
            metric=task_handler_errors,
            threshold=5,
            evaluation_periods=2,
            alarm_description='Task handler error rate is too high',
        )

        cloudwatch.Alarm(
            self,
            'ApiGateway5xxAlarm',
            metric=api_5xx_errors,
            threshold=10,
            evaluation_periods=2,
            alarm_description='API Gateway 5xx error rate is too high',
        )
