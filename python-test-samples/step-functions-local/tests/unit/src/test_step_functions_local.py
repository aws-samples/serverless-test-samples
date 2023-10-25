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


@pytest.fixture(scope="session")
def container(request):
    """
    Runs the amazon/aws-stepfunctions-local container with the MockConfigFile.json
    """

    mock_file_host_path = os.path.join(os.path.dirname(__file__), '..', '..', '..',
                                       'statemachine', 'test', 'MockConfigFile.json')
    mock_file_container_path = "/home/stepfunctionslocal/MockConfigFile.json"

    container = DockerContainer("amazon/aws-stepfunctions-local") \
        .with_bind_ports(8083, 8083) \
        .with_exposed_ports(8083) \
        .with_env("SFN_MOCK_CONFIG", mock_file_container_path) \
        .with_volume_mapping(mock_file_host_path, mock_file_container_path)

    container.start()
    wait_for_logs(container, "Starting server on port 8083")

    # Important to avoid non-deterministic behavior, waiting for container to spin up
    time.sleep(2)

    def stop_step_function():
        log.info("[fixture] stopping step functions container")
        container.stop()

    request.addfinalizer(stop_step_function)

    return container


@pytest.fixture(scope="session", autouse=True)
def sfn_client(request, container):
    """
    Creates the state machine using the local_testing.asl.json definition
    """

    # Set up Step Function client with test container URL
    sfn_client = boto3.client('stepfunctions',
        endpoint_url='http://' + container.get_container_host_ip() + ':' + container.get_exposed_port(8083))

    # Read state machine definition
    step_function_definition = Path(
        os.path.join(os.path.dirname(__file__), '..', '..', '..', 'statemachine', 'local_testing.asl.json')).read_text()

    # Create state machine
    try:
        sfn_client.create_state_machine(
            name="LocalTesting",
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
    else:
        return sfn_client


def get_arn(sfn_client):
    """
    Get state machine ARN
    """
    state_machine_arn = sfn_client.list_state_machines()["stateMachines"][0]["stateMachineArn"]

    return state_machine_arn


def execute_stepfunction(sfn_client, execution_name, test_name):
    """
    Executes the step function passing in valid_input.json
    Returns a history of the state transitions once the step function is complete

    @param: test_name - Used to look up the test case and mocks to use in MockConfigFile.json
    """
    state_machine_arn = get_arn(sfn_client)

    step_function_input = Path(
        os.path.join(os.path.dirname(__file__), '../../..', 'statemachine', 'test', 'valid_input.json')).read_text()

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
            history_response = sfn_client.get_execution_history(executionArn=start_execution['executionArn'])
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
    Testing that the step function completes successfully.
    Every external service runs succesfully and the state machine exits with "CustomerAddedToFollowup".
    """
    history_response = execute_stepfunction(sfn_client, 'happyPathExecution', 'HappyPathTest')

    assert check_state_exited_event_details(history_response, 'CustomerAddedToFollowup')


def test_negative_sentiment(sfn_client):
    """
    Testing that the step function completes successfully.
    The contact details are properly formatted, a negative sentiment is detected within the user comments and the state
    machine exits with "NegativeSentimentDetected"
    """
    history_response = execute_stepfunction(sfn_client, 'negativeSentimentExecution', 'NegativeSentimentTest')

    assert check_state_exited_event_details(history_response, 'NegativeSentimentDetected')


def test_retry_on_service_exception(sfn_client):
    """
    Testing that the step function completes successfully after retrying
    The sentiment detection service fails three times and the state machine retries until successfully retrieving the
    sentiment on the fourth attempt.
    """
    history_response = execute_stepfunction(sfn_client, 'retryExecution', 'RetryOnServiceExceptionTest')

    results = []
    for event in history_response['events']:
        if (event['type'] == 'TaskFailed' and 'taskFailedEventDetails' in event and
            event['taskFailedEventDetails']['error'] == 'InternalServerException'
            ) or (
                event['type'] == 'TaskSucceeded' and 'taskSucceededEventDetails' in event and
                event['taskSucceededEventDetails']['resource'] == 'comprehend:detectSentiment'
        ):
            results.append(event)

    assert len(results) == 4

    internal_error_count = 0
    for event in results[0:3]:
        if event['type'] == 'TaskFailed' and 'taskFailedEventDetails' in event and \
                event['taskFailedEventDetails']['error'] == 'InternalServerException':
            internal_error_count += 1

    assert internal_error_count == 3

    last_event = results[3]
    assert last_event['taskSucceededEventDetails']['resource'] == 'comprehend:detectSentiment'
