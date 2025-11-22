#!/usr/bin/env python3
"""CDK app entry point for CNS427 Task Management API."""

import os

import aws_cdk as cdk
from cdk_nag import AwsSolutionsChecks, NagReportFormat

from infrastructure.core.task_api_stack import TaskApiCoreStack, TaskApiMonitoringStack, TaskApiStack

app = cdk.App()

# Environment configuration
env = cdk.Environment(account=app.node.try_get_context('account'), region=app.node.try_get_context('region') or 'us-east-1')

# Stack naming
stack_prefix = app.node.try_get_context('stack_prefix') or 'cns427-task-api'

# Core infrastructure stack
core_stack = TaskApiCoreStack(app, f'{stack_prefix}-core', env=env, description='Core infrastructure for CNS427 Task Management API')

# API stack
api_stack = TaskApiStack(app, f'{stack_prefix}-api', core_stack=core_stack, env=env, description='API infrastructure for CNS427 Task Management API')

# Monitoring stack
monitoring_stack = TaskApiMonitoringStack(
    app, f'{stack_prefix}-monitoring', api_stack=api_stack, env=env, description='Monitoring and observability for CNS427 Task Management API'
)

# Add dependencies
api_stack.add_dependency(core_stack)
monitoring_stack.add_dependency(api_stack)

# CDK Nag Security Checks (Conditional)
# Enable with: ENABLE_CDK_NAG=true cdk synth
# Or via context: cdk synth -c enable-cdk-nag=true
enable_cdk_nag = os.getenv('ENABLE_CDK_NAG', '').lower() == 'true' or app.node.try_get_context('enable-cdk-nag')
enable_reports = os.getenv('CDK_NAG_REPORT', '').lower() == 'true' or app.node.try_get_context('cdk-nag-report')

if enable_cdk_nag:
    print('🔒 CDK Nag: Enabled - Running AwsSolutions security checks...')

    # Configure report formats if requested
    report_formats = []
    if enable_reports:
        report_formats = [NagReportFormat.CSV, NagReportFormat.JSON]
        print('📊 CDK Nag: Report generation enabled (CSV + JSON)')

    # Apply AwsSolutions checks to all stacks
    cdk.Aspects.of(app).add(AwsSolutionsChecks(verbose=True, reports=enable_reports, report_formats=report_formats if report_formats else None))
else:
    print('ℹ️  CDK Nag: Disabled (set ENABLE_CDK_NAG=true to enable)')

app.synth()
