# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""Tests Step Functions local with mocks using pytest"""
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
    Runs the amazon/aws-stepfunctions-local container without the MockConfigFile
    """
    sf_local = DockerContainer("amazon/aws-stepfunctions-local") \
        .with_bind_ports(8083, 8083) \
        .with_exposed_ports(8083)
    
    # Start the container
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
            name="HelloWorldStateMachine",
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

def execute_stepfunction(sfn_client, execution_name, test_name=None):
    """
    Executes the step function with an empty input
    Returns a history of the state transitions once the step function is complete
    
    @param: test_name - No longer used with simple Hello World example
    """
    state_machine_arn = get_arn(sfn_client)

    # Empty input is sufficient for Hello World Pass state
    step_function_input = "{}"

    try:
        # Starting execution of the state machine
        start_execution = sfn_client.start_execution(
            name=execution_name,
            stateMachineArn=state_machine_arn,  # No longer appending test_name
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


def check_state_exited_event_details(history_response, state_name):
    """
    Test utility - checks if a state with the given name was exited during execution
    Works with any state type (Pass, Task, etc.)
    """
    for event in history_response['events']:
        if 'stateExitedEventDetails' in event and event['stateExitedEventDetails']['name'] == state_name:
            return True
    
    return False

def test_happy_path(sfn_client):
    """
    Testing that the hello world step function completes successfully.
    Verifies that the state machine exits from the HelloWorld state.
    """
    history_response = execute_stepfunction(sfn_client, 'happyPathExecution')

    # Check if execution succeeded
    execution_succeeded = False
    for event in history_response['events']:
        if event['type'] == 'ExecutionSucceeded':
            execution_succeeded = True
            break
    
    assert execution_succeeded, "Step function execution did not succeed"
    
    # Check if HelloWorld state was exited
    assert check_state_exited_event_details(history_response, 'HelloWorld'), "HelloWorld state was not exited"