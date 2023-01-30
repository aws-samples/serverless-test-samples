# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import uuid
import boto3
from datetime import datetime, timedelta
import pytest
import backoff

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

dynamodb = boto3.client('dynamodb')
s3 = boto3.client('s3')
cloudformation = boto3.client("cloudformation")
poll_timeout_duration_secs = 10

'''@pytest.fixture
def poll_timeout_duration_secs():
    # set timeout duration to be your SLA 
    return 10'''

# generate a random filename
class SingletonFilename(object):
    file_name = ""
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingletonFilename, cls).__new__(cls)
            cls.value = str(uuid.uuid4()) + ".txt"
        return cls.instance

file_name = SingletonFilename()

# return the filename as a fixture
@pytest.fixture()
def test_filename():
    singleton = SingletonFilename()
    return singleton.value

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
        src_bucket_name = source_bucket_output[0]["OutputValue"]
        yield src_bucket_name # teardown code for fixtures is run after the yield statement
    except KeyError as e:
        raise Exception(
            f"Cannot find output SourceBucketName in stack {source_bucket_output}"
        ) from e

    try: 
        stack_outputs = stacks[0]["Outputs"]
        source_bucket_output = [output for output in stack_outputs if output["OutputKey"] == "DestinationBucketName"]
        destination_bucket_name = source_bucket_output[0]["OutputValue"]
    except KeyError as e:
        raise Exception(
            f"Cannot find output DestinationBucketName in stack {destination_bucket_name}"
        ) from e

    # cleanup source bucket
    print("*** Cleanup - removing object from S3 source table... ")
    
    response = s3.delete_object(Bucket=src_bucket_name, Key=file_name.value)
    if response['ResponseMetadata']['HTTPStatusCode'] != 204:
        raise Exception(
            f"Cannot delete {file_name.value} from {src_bucket_name}. Response: " + str(response)
        )

    # cleanup destination bucket
    print("*** Cleanup - removing object from S3 destination table... ")
    response = s3.delete_object(Bucket=destination_bucket_name, Key=file_name.value)
    if response['ResponseMetadata']['HTTPStatusCode'] != 204:
        raise Exception(
            f"Cannot delete {file_name.value} from {destination_bucket_name}. Response: " + str(response)
        )


# get the name of the destination dynamodb table where the results should be
@pytest.fixture
def test_results_table() -> str:
    stacks = getStacks()
    try: 
        stack_outputs = stacks[0]["Outputs"]
        async_test_results_output = [output for output in stack_outputs if output["OutputKey"] == "AsyncTransformTestResultsTable"]
        table_name = async_test_results_output[0]["OutputValue"]
        yield table_name # teardown code for fixtures is run after the yield statement
    except KeyError as e:
        raise Exception(
            f"Cannot find output AsyncTransformTestResultsTable in stack {async_test_results_output}"
        ) from e

    # cleanup from results table
    print("\n*** Cleanup - removing item from DynamoDB results table... ")

    response = dynamodb.delete_item(TableName=table_name, Key={'id':{'S':file_name.value}}, ReturnValues="ALL_OLD")
 
    try:
        # if this attribute is not present, the delete_item command did not find the row to delete 
        response['Attributes']['message']
    except KeyError as e:
        raise Exception(
            f"Cannot delete {file_name.value} from {table_name}. Response: " + str(response)
        )

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

    try:
        response = cloudformation.describe_stacks(StackName=stack_name)
    except Exception as e:
        raise Exception(
            f"Cannot find stack {stack_name}. \n" f'Please make sure stack with the name "{stack_name}" exists.'
        ) from e

    return response["Stacks"]

'''
Put a lowercase string into the source bucket. 
This the is beginning of the async process. 
'''
def put_object_into_source_bucket(unmodified_message, source_bucket_name, test_filename):

    print() # make output pretty
    print("*** Putting object into S3... ")
    response = s3.put_object(Body=unmodified_message, Bucket=source_bucket_name, Key=test_filename)
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise f"Cannot put object into Source Bucket {source_bucket_name}"


'''
Implement a backoff and set the maximum amount of time to poll.
This can be based on our system's SLA.
'''
@backoff.on_exception(backoff.fibo,
                      (KeyError), 
                      max_time=poll_timeout_duration_secs)
def poll_for_file(test_results_table, test_filename, modified_message):

    msg = "*** Querying DynamoDB for the object. "

    # query dynamodb for the output
    response = dynamodb.get_item(
        TableName=test_results_table,
        Key={
            'id': {'S': test_filename}
        }
    )

    try:
        # did we get the object?
        x = response['Item']['message']
    except KeyError:
        print(msg + "Could not find result...")
        raise KeyError

    # is the object formed correctly?
    if x['S'] != modified_message:
        print(f"Object malformed. Found {x['S']}. Should be: {modified_message}")
        return False

    print (msg + "Found the result. Success!")
    return True
    
'''
Poll to retrieve the modified string from a DynamoDB table at the end of the async process.
'''    
def test_retrieve_object_from_dynamodb(unmodified_message, modified_message, source_bucket_name, test_results_table, test_filename):

    put_object_into_source_bucket(unmodified_message, source_bucket_name, test_filename)
    
    try:
        poll_for_file(test_results_table, test_filename, modified_message), f"DynamoDB poller timed out."
    except:
        raise Exception("DynamoDB poller timed out.")

    return True

# TODO README, test prod deploy