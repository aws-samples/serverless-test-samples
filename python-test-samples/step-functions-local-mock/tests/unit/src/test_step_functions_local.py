"""Tests Step Functions local with mocks using pytest for LambdaSQSIntegration"""
import os
import time
import logging
from pathlib import Path
import pytest
import boto3
from botocore.exceptions import ClientError
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs

log = logging.getLogger()


@pytest.fixture(name="container", scope="session")
def fixture_container(request):
    """
    Runs the amazon/aws-stepfunctions-local container with the MockConfigFile.json
    """

    mock_file_host_path = os.path.join(os.path.dirname(__file__), '..', '..', '..',
                                       'statemachine', 'test', 'MockConfigFile.json')
    mock_file_container_path = "/home/stepfunctionslocal/MockConfigFile.json"

    sf_local = DockerContainer("amazon/aws-stepfunctions-local") \
        .with_bind_ports(8083, 8083) \
        .with_exposed_ports(8083) \
        .with_env("SFN_MOCK_CONFIG", mock_file_container_path) \
        .with_volume_mapping(mock_file_host_path, mock_file_container_path)

    sf_local.start()
    wait_for_logs(sf_local, "Starting server on port 8083")

    # Important to avoid non-deterministic behavior, waiting for container to spin up
    time.sleep(2)

    def stop_step_function():
        log.info("[fixture] stopping step functions container")
        sf_local.stop()

    request.addfinalizer(stop_step_function)

    return sf_local


@pytest.fixture(name="sfn_client", scope="session", autouse=True)
def fixture_sfn_client(container):
    """
    Creates the state machine using the local_testing.asl.json definition
    """
        
    # Set up Step Function client with test container URL
    client = boto3.client('stepfunctions',
        endpoint_url='http://' + container.get_container_host_ip() + ':' +
                     container.get_exposed_port(8083))

    # Read state machine definition
    step_function_definition = Path(
        os.path.join(os.path.dirname(__file__), '..', '..', '..', 'statemachine',
                     'local_testing.asl.json')).read_text(encoding="utf-8")

    # Create state machine
    try:
        client.create_state_machine(
            name="LambdaSQSIntegration",
            definition=step_function_definition,
            roleArn="arn:aws:iam::123456789012:role/DummyRole"
        )
    except ClientError as err:
        log.error(
            "Couldn't create state machine. Here's why: %s: %s",
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise

    return client


def get_arn(sfn_client):
    """
    Get state machine ARN
    """
    state_machine_arn = sfn_client.list_state_machines()["stateMachines"][0]["stateMachineArn"]

    return state_machine_arn


def execute_stepfunction(sfn_client, execution_name, test_name):
    """
    Executes the step function with a sample input
    Returns a history of the state transitions once the step function is complete

    @param: test_name - Used to look up the test case and mocks to use in MockConfigFile.json
    """
    state_machine_arn = get_arn(sfn_client)

    # Simple input for the state machine
    step_function_input = '{"data": "test input"}'

    try:
        # Starting execution of the state machine
        start_execution = sfn_client.start_execution(
            name=execution_name,
            stateMachineArn=state_machine_arn + '#' + test_name,
            input=step_function_input
        )
    except ClientError as err:
        log.error(
            "Couldn't start state machine %s. Here's why: %s: %s",
            state_machine_arn,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise

    while True:
        time.sleep(1)

        # Checking whether the execution has completed.
        try:
            history_response = sfn_client.get_execution_history(
                executionArn=start_execution['executionArn'])
        except ClientError as err:
            log.error(
                "Couldn't fetch execution history for state machine %s. Here's why: %s: %s",
                state_machine_arn,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

        success = False
        for event in history_response['events']:
            if event['type'] == 'ExecutionSucceeded':
                success = True
                break

        if success:
            break

    return history_response


def check_state_exited_event_details(history_response, state_exited_event_details):
    """
    Test utility - used to verify which state the task exited in
    """
    success = False

    for event in history_response['events']:
        if event['type'] == 'TaskStateExited' and 'stateExitedEventDetails' in event and \
                event['stateExitedEventDetails']['name'] == state_exited_event_details:
            success = True
            break

    return success


def test_happy_path(sfn_client):
    """
    Testing the happy path where both Lambda and SQS operations succeed on the first try.
    """
    history_response = execute_stepfunction(sfn_client, 'happyPathExecution', 'HappyPath')

    # Check that both states exited successfully
    assert check_state_exited_event_details(history_response, 'LambdaState')
    assert check_state_exited_event_details(history_response, 'SQSState')

    # Count task states that were successful
    success_count = 0
    for event in history_response['events']:
        if event['type'] == 'TaskSucceeded':
            success_count += 1

    # We expect both Lambda and SQS tasks to succeed
    assert success_count == 2


def test_retry_path(sfn_client):
    """
    Testing retry path where Lambda fails multiple times before succeeding.
    The Lambda invocation is retried until it succeeds on the 4th attempt.
    """
    history_response = execute_stepfunction(sfn_client, 'retryPathExecution', 'RetryPath')

    # Check that both states exited successfully
    assert check_state_exited_event_details(history_response, 'LambdaState')
    assert check_state_exited_event_details(history_response, 'SQSState')

    # Count Lambda failures
    lambda_failures = 0
    resource_not_ready_errors = 0
    timeout_errors = 0
    
    for event in history_response['events']:
        if event['type'] == 'TaskFailed':
            lambda_failures += 1
            if 'taskFailedEventDetails' in event:
                error = event['taskFailedEventDetails']['error']
                if error == 'Lambda.ResourceNotReadyException':
                    resource_not_ready_errors += 1
                elif error == 'Lambda.TimeoutException':
                    timeout_errors += 1

    # There should be three failures (1 ResourceNotReady, 2 Timeout) before success
    assert lambda_failures == 3
    assert resource_not_ready_errors == 1
    assert timeout_errors == 2


def test_hybrid_path(sfn_client):
    """
    Testing hybrid path where only Lambda state is mocked and SQS uses 
    the mock that was specified in the default configuration.
    """
    history_response = execute_stepfunction(sfn_client, 'hybridPathExecution', 'HybridPath')

    # Verify that the execution completed successfully
    execution_succeeded = False
    for event in history_response['events']:
        if event['type'] == 'ExecutionSucceeded':
            execution_succeeded = True
            break
    
    assert execution_succeeded, "Execution did not complete successfully"
    
    # If the execution completed successfully, and we've verified the state transitions,
    # we can assume the Lambda was successful
    assert check_state_exited_event_details(history_response, 'LambdaState')
    assert check_state_exited_event_details(history_response, 'SQSState')