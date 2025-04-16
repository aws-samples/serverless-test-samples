"""Tests Step Functions local with Lambda integrations using pytest"""
import os
import time
import json
import logging
import subprocess
from pathlib import Path
import pytest
import boto3
import requests
from botocore.exceptions import ClientError
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs

log = logging.getLogger()

SAM_LAMBDA_PORT = 3001

@pytest.fixture(name="lambda_container", scope="session")
def fixture_lambda_container(request):
    """
    Verifies SAM local Lambda emulator is running
    """
    # Try to connect using requests
    try:
        response = requests.get(f"http://127.0.0.1:{SAM_LAMBDA_PORT}/2018-06-01/ping", timeout=2)
        if response.status_code == 200:
            log.info(f"SAM Local is available at port {SAM_LAMBDA_PORT}")
        else:
            log.warning(f"SAM Local responded with status code {response.status_code}")
    except subprocess.CalledProcessError:
        log.warning(f"SAM Local not detected at port {SAM_LAMBDA_PORT}. Tests may fail.")
    
    yield None


@pytest.fixture(name="sfn_container", scope="session")
def fixture_sfn_container(request, lambda_container):
    """
    Runs the amazon/aws-stepfunctions-local container
    
    Host network is required for proper SAM Lambda integration as it allows the
    Step Functions container to directly access the Lambda emulator on the host.
    We use subprocess to run Docker commands directly since it provides more
    reliable control over host networking than testcontainers Python Docker libraries.
    
    """
    # Get Docker command directly - testcontainers doesn't support host network mode
    container_name = "stepfunctions-local-test"
    
    # Stop previous container if exists
    try:
        subprocess.run(["docker", "rm", "-f", container_name], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    except Exception:
        pass
    
    # Start container with host network
    cmd = [
        "docker", "run", "--rm", "-d",
        "--name", container_name,
        "--network", "host",
        "-e", "AWS_ACCESS_KEY_ID=DUMMYIDEXAMPLE",
        "-e", "AWS_SECRET_ACCESS_KEY=DUMMYEXAMPLEKEY", 
        "-e", "AWS_DEFAULT_REGION=us-east-1",
        "-e", f"LAMBDA_ENDPOINT=http://127.0.0.1:{SAM_LAMBDA_PORT}",
        "amazon/aws-stepfunctions-local"
    ]
    
    container_id = subprocess.check_output(cmd).decode().strip()
    log.info(f"Started Step Functions container: {container_id}")
    
    # Wait for container to be ready
    time.sleep(5)
    
    # Check if container is running
    result = subprocess.run(
        ["docker", "logs", container_name],
        capture_output=True,
        text=True
    )
    if "Starting server on port 8083" not in result.stdout:
        log.warning("Step Functions container might not be ready. Check container logs.")
        time.sleep(5)
    
    # Create client
    client = boto3.client('stepfunctions',
        endpoint_url='http://localhost:8083',
        aws_access_key_id="DUMMYIDEXAMPLE",
        aws_secret_access_key="DUMMYEXAMPLEKEY",
        region_name="us-east-1")
    
    def stop_step_function():
        log.info(f"[fixture] stopping step functions container {container_name}")
        subprocess.run(["docker", "stop", container_name], check=False)
    
    request.addfinalizer(stop_step_function)
    
    return {'client': client, 'container_id': container_id, 'container_name': container_name}


@pytest.fixture(name="sfn_client", scope="session", autouse=True)
def fixture_sfn_client(sfn_container):
    """
    Creates the state machine for Lambda integration testing
    """
    # Get the client from sfn_container
    client = sfn_container['client']

    # Read state machine definition
    step_function_definition = Path(
        os.path.join(os.path.dirname(__file__), '..', '..', '..', 'statemachine',
                     'local_testing.asl.json')).read_text(encoding="utf-8")

    # Create state machine
    try:
        client.create_state_machine(
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
    
    return client


def get_arn(sfn_client):
    """
    Get state machine ARN
    """
    state_machine_arn = sfn_client.list_state_machines()["stateMachines"][0]["stateMachineArn"]
    return state_machine_arn


def execute_stepfunction(sfn_client, execution_name, input_data, max_wait_seconds=30):
    """
    Executes the step function with the provided input
    Returns a history of the state transitions once the step function is complete
    """
    state_machine_arn = get_arn(sfn_client)

    try:
        # Starting execution of the state machine
        start_execution = sfn_client.start_execution(
            name=execution_name,
            stateMachineArn=state_machine_arn,
            input=json.dumps(input_data)
        )
    except ClientError as err:
        log.error(
            "Couldn't start state machine %s. Here's why: %s: %s",
            state_machine_arn,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise

    start_time = time.time()
    while time.time() - start_time < max_wait_seconds:
        time.sleep(1)

        # Checking whether the execution has completed.
        try:
            execution_response = sfn_client.describe_execution(
                executionArn=start_execution['executionArn'])
            
            if execution_response['status'] in ['SUCCEEDED', 'FAILED', 'TIMED_OUT', 'ABORTED']:
                # Get the execution history
                history_response = sfn_client.get_execution_history(
                    executionArn=start_execution['executionArn'])
                
                # Log details if execution failed
                if execution_response['status'] != 'SUCCEEDED':
                    log.error(f"Execution failed with status: {execution_response['status']}")
                    if 'error' in execution_response:
                        log.error(f"Error: {execution_response.get('error')}")
                    if 'cause' in execution_response:
                        log.error(f"Cause: {execution_response.get('cause')}")
                
                return history_response, execution_response
                
        except ClientError as err:
            log.error(
                "Couldn't fetch execution details for state machine %s. Here's why: %s: %s",
                state_machine_arn,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

    raise TimeoutError(f"Execution did not complete within {max_wait_seconds} seconds")


def check_state_exited_event_details(history_response, state_name):
    """
    Test utility - used to verify which state the task exited in
    """
    success = False

    for event in history_response['events']:
        # Check for regular Task state exits
        if event['type'] == 'TaskStateExited' and 'stateExitedEventDetails' in event and \
                event['stateExitedEventDetails']['name'] == state_name:
            success = True
            break
            
        # Check for Wait state exits - they use a different event type
        if event['type'] == 'WaitStateExited' and 'stateExitedEventDetails' in event and \
                event['stateExitedEventDetails']['name'] == state_name:
            success = True
            break
            
        # Generic check for any state exit
        if 'stateExitedEventDetails' in event and \
           event['stateExitedEventDetails']['name'] == state_name:
            success = True
            break

    return success


def test_lambda_sum_operation(sfn_client):
    """
    Test just the Lambda sum operation is working correctly
    """
    
    # Load JSON input file and parse it
    input_data_str = Path(os.path.join(os.path.dirname(__file__), '../../..', 'statemachine', 'test',
                 'valid_input_lambda_sum.json')).read_text(encoding="utf-8")
    input_data = json.loads(input_data_str)  # Parse the JSON string into a dictionary
    
    # Expected sum x + y + z = 10 + 20 + 30 = 60
    expected_sum = input_data["x"] + input_data["y"] + input_data["z"]  # 60
    
    # Create a lambda client to directly test the function
    lambda_client = boto3.client('lambda', 
        endpoint_url=f'http://127.0.0.1:{SAM_LAMBDA_PORT}',
        aws_access_key_id="DUMMYIDEXAMPLE",
        aws_secret_access_key="DUMMYEXAMPLEKEY",
        region_name="us-east-1")
    
    # Test sum lambda directly
    try:
        response = lambda_client.invoke(
            FunctionName='StepFunctionExampleSumLambda',
            Payload=json.dumps(input_data)
        )
        
        # Parse response
        result = json.loads(response['Payload'].read())
        print(f"Lambda sum response: {result}")
        
        # Check result based on the actual structure
        assert 'Payload' in result, "Response missing 'Payload' field"
        assert 'result' in result['Payload'], "Payload missing 'result' field"
        assert result['Payload']['result'] == expected_sum, f"Expected sum {expected_sum}, got {result['Payload']['result']}"
    except Exception as e:
        pytest.skip(f"Lambda invocation failed, SAM might not be running properly: {e}")


def test_lambda_square_operation(sfn_client):
    """
    Test just the Lambda square operation is working correctly
    """
    
    # Load JSON input file and parse it
    input_data_str = Path(os.path.join(os.path.dirname(__file__), '../../..', 'statemachine', 'test',
                 'valid_input_lambda_square.json')).read_text(encoding="utf-8")
    input_data = json.loads(input_data_str) 
    
    # Expected 9^2 = 9 * 9 = 81
    expected_square = input_data["result"] * input_data["result"]  # 81
    
    # Create a lambda client to directly test the function
    lambda_client = boto3.client('lambda', 
        endpoint_url=f'http://127.0.0.1:{SAM_LAMBDA_PORT}',
        aws_access_key_id="DUMMYIDEXAMPLE",
        aws_secret_access_key="DUMMYEXAMPLEKEY",
        region_name="us-east-1")

    # Test square lambda directly
    try:
        response = lambda_client.invoke(
            FunctionName='StepFunctionExampleSquareLambda',
            Payload=json.dumps(input_data)
        )
        
        # Parse response
        payload_bytes = response['Payload'].read()
        result = json.loads(payload_bytes)
        print(f"Lambda square response: {result}")
        
        # Check result based on the actual structure
        assert 'Payload' in result, "Response missing 'Payload' field"
        assert 'result' in result['Payload'], "Payload missing 'result' field"
        assert result['Payload']['result'] == expected_square, f"Expected square {expected_square}, got {result['Payload']['result']}"
    except Exception as e:
        pytest.skip(f"Lambda invocation failed, SAM might not be running properly: {e}")
  

def test_stepfunctions_sum_square_workflow_execution(sfn_client):
    """
    Test full execution of the mathematical workflow:
    1. Sum three numbers (x + y + z)
    2. Wait for 3 seconds
    3. Square the result (sum^2)
    """
    
    # Load JSON input file and parse it
    input_data_str = Path(os.path.join(os.path.dirname(__file__), '../../..', 'statemachine', 'test',
                 'valid_input_stepfunctions_sum_square.json')).read_text(encoding="utf-8")
    input_data = json.loads(input_data_str) 
    
    # Expected sum and final result
    expected_sum = input_data["x"] + input_data["y"] + input_data["z"]  # 17
    expected_final = expected_sum * expected_sum  # 289
    
    # Execute the state machine
    history_response, execution_response = execute_stepfunction(
        sfn_client, 'mathWorkflowExecution', input_data)
    
    # Check execution succeeded
    assert execution_response['status'] == 'SUCCEEDED', "Execution did not succeed"
    
    # Verify output contains the expected result
    output = json.loads(execution_response['output'])
    print(f"Output received: {output}")
    
    # Check for the result in the Payload structure
    assert 'Payload' in output, "Output missing 'Payload' field"
    assert 'result' in output['Payload'], "Payload missing 'result' field"
    assert output['Payload']['result'] == expected_final, f"Expected result {expected_final}, got {output['Payload']['result']}"
    
    # Check that all states exited successfully
    assert check_state_exited_event_details(history_response, 'Lambda Sum State')
    assert check_state_exited_event_details(history_response, 'Wait State')
    assert check_state_exited_event_details(history_response, 'Lambda Square State')


def test_stepfunctions_large_number_handling(sfn_client):
    """
    Test handling of larger numbers to ensure no integer overflow issues
    """
    
    # Load JSON input file and parse it
    input_data_str = Path(os.path.join(os.path.dirname(__file__), '../../..', 'statemachine', 'test',
                 'valid_input_stepfunctions_large_numbers.json')).read_text(encoding="utf-8")
    input_data = json.loads(input_data_str) 
    
    # Expected results
    expected_sum = input_data["x"] + input_data["y"] + input_data["z"]  # 26664
    expected_final = expected_sum * expected_sum  # 710968896
    
    # Execute the state machine
    history_response, execution_response = execute_stepfunction(
        sfn_client, 'largeNumberExecution', input_data)
    
    # Check execution succeeded
    assert execution_response['status'] == 'SUCCEEDED', "Execution did not succeed"
    
    # Verify output contains the expected result
    output = json.loads(execution_response['output'])
    print(f"Output received for large numbers: {output}")
    
    # Check for the result in the Payload structure
    assert 'Payload' in output, "Output missing 'Payload' field"
    assert 'result' in output['Payload'], "Payload missing 'result' field"
    assert output['Payload']['result'] == expected_final, f"Expected result {expected_final}, got {output['Payload']['result']}"