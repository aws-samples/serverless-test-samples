# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import uuid
import boto3
from datetime import datetime, timedelta
import pytest

'''
usage:

Set the environment variable AWS_SAM_STACK_NAME to match the name of the stack you will test
-- or -- 
add AWS_SAM_STACK_NAME to the beginning of your command

example:
async-lambda-dynamodb$ AWS_SAM_STACK_NAME=<stack-name> python -m pytest -s tests/integration -v
'''

'''
Asynchronous systems may have service level agreements (SLA's) for the latency of a 
given process. When you test the system, you can use this SLA to set the timeout 
duration for your test. If you do not have an explicit SLA, you may set the timeout 
duration to be some reasonable amount that you would expect the system to complete 
the process.    
'''
@pytest.fixture
def poll_timeout_duration_secs():
    # set timeout duration to your SLA guarantee
    return 10

# generate a random filename
file_name = ""
@pytest.fixture()
def test_filename():
    global file_name
    if file_name == "":
        file_name=str(uuid.uuid4()) + ".txt"

# message before the async process transforms it
@pytest.fixture
def unmodified_message():
    return "this message was created during an integration test"

# expected message after the async process transforms it
@pytest.fixture()
def modified_message():
    return "THIS MESSAGE WAS CREATED DURING AN INTEGRATION TEST"

# get the name of the source S3 bucket
@pytest.fixture
def source_bucket_name() -> str:
    stacks = getStacks()
    try: 
        stack_outputs = stacks[0]["Outputs"]
        source_bucket_output = [output for output in stack_outputs if output["OutputKey"] == "SourceBucketName"]
        return source_bucket_output[0]["OutputValue"]
    except KeyError as e:
        raise Exception(
            f"Cannot find output SourceBucketName in stack {source_bucket_output}"
        ) from e

# get the name of the destination dynamodb table where the results should be
@pytest.fixture
def test_results_table() -> str:
    stacks = getStacks()
    try: 
        stack_outputs = stacks[0]["Outputs"]
        async_test_results_output = [output for output in stack_outputs if output["OutputKey"] == "AsyncTransformTestResultsTable"]
        return async_test_results_output[0]["OutputValue"]
    except KeyError as e:
        raise Exception(
            f"Cannot find output AsyncTransformTestResultsTable in stack {async_test_results_output}"
        ) from e

'''
Based on the provided AWS_SAM_STACK_NAME, we can use CloudFormation API 
to find out the S3 SourceBucket name where the initial data will be put, 
as well as the DynamoDB TableName where the modified data will eventually 
reside at the end of the process.
'''
def getStacks() -> str:

    stack_name = os.environ.get("AWS_SAM_STACK_NAME")
    if not stack_name:
        raise Exception(
            "Cannot find env var AWS_SAM_STACK_NAME. \n"
            "Please include the stack name when running integration tests."
        )

    client = boto3.client("cloudformation")

    try:
        response = client.describe_stacks(StackName=stack_name)
    except Exception as e:
        raise Exception(
            f"Cannot find stack {stack_name}. \n" f'Please make sure stack with the name "{stack_name}" exists.'
        ) from e

    return response["Stacks"]

'''
Put a lowercase string into the source bucket. 
This the is beginning of the production async process. 
'''
def put_object_into_source_bucket(unmodified_message, source_bucket_name, file_name):

    print()
    print("Putting object into S3...")
    client = boto3.client('s3')
    response = client.put_object(Body=unmodified_message, Bucket=source_bucket_name, Key=file_name)
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise f"Cannot put object into Source Bucket {source_bucket_name}"

'''
Poll to retrieve the modified string from a DynamoDB Table. This is the end of the async process.
'''    
def test_retrieve_object_from_dynamodb(unmodified_message, modified_message, source_bucket_name, test_results_table, poll_timeout_duration_secs, test_filename):

    print()
    # set the maximum amount of time to poll before the test fails
    # this can be based on our system's SLA
    loop_start_time = datetime.now()
    loop_max_time = loop_start_time + timedelta(seconds=poll_timeout_duration_secs)
    global file_name

    put_file_yet = False

    while True:

        if put_file_yet == False:
            put_object_into_source_bucket(unmodified_message, source_bucket_name, file_name)
            put_file_yet = True
            
        # query dynamodb for the output
        dynamodb = boto3.client("dynamodb")
        response = dynamodb.get_item(
            TableName=test_results_table,
            Key={
                'id': {'S': file_name}
            }
        )

        # did we get the object?
        try: 
            x = response['Item']['message']
            print("*** Object found in DynamoDB. Success! ***")

            # is the object formed correctly?
            assert x['S'] == modified_message, f"Object malformed. Found {x}. Should be: {modified_message}"
            
            # we found the object and it's well formed, let's get out of here
            break

        except KeyError:
            pass
        
        print("Querying DynamoDB for modified object. Not found yet...")
        
        if (loop_max_time < datetime.now()):
            assert False, ("Could not retrieve object from DynamoDB before timeout. Async process failed.")
