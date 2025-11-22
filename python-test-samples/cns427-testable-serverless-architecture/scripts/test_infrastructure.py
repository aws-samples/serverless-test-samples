"""Test infrastructure management utilities."""

import os
from typing import Dict

import boto3


def verify_deployment() -> Dict[str, bool]:
    """
    Verify test infrastructure deployment status.

    Returns:
        Dictionary with deployment status of each component.
    """
    region = os.environ.get('AWS_DEFAULT_REGION', os.environ.get('AWS_REGION', 'us-west-2'))
    stack_name = os.environ.get('TEST_INFRASTRUCTURE_STACK_NAME', 'CNS427TaskApiTestInfrastructure')
    cfn = boto3.client('cloudformation', region_name=region)

    try:
        response = cfn.describe_stacks(StackName=stack_name)
        stack_status = response['Stacks'][0]['StackStatus']

        # Stack exists and is in a good state
        stack_deployed = stack_status in ['CREATE_COMPLETE', 'UPDATE_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE']

        return {
            'test_infrastructure_stack': stack_deployed,
            'test_results_table': stack_deployed,  # Exists if stack exists
            'test_subscriber_lambda': stack_deployed,  # Exists if stack exists
            'test_event_rule': stack_deployed,  # Exists if stack exists
        }
    except cfn.exceptions.ClientError:
        # Stack doesn't exist
        return {
            'test_infrastructure_stack': False,
            'test_results_table': False,
            'test_subscriber_lambda': False,
            'test_event_rule': False,
        }
    except Exception as e:
        # Other error (credentials, network, etc.)
        print(f'Error checking test infrastructure: {e}')
        return {
            'test_infrastructure_stack': False,
            'test_results_table': False,
            'test_subscriber_lambda': False,
            'test_event_rule': False,
        }
