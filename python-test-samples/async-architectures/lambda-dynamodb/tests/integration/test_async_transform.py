# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import uuid
from unittest import TestCase
import boto3
import requests
from datetime import datetime, timedelta

"""
usage:

Set the environment variable AWS_SAM_STACK_NAME to match the name of the stack you will test
-- or -- 
add AWS_SAM_STACK_NAME to the beginning of your command

example:
AWS_SAM_STACK_NAME=<stack-name> python -m pytest -s tests/integration -v
"""

class TestAsynchronousTransformation(TestCase):

    """
    Asynchronous systems may have service level agreements (SLA's) for the latency of a 
    given process. When you test the system, you can use this SLA to set the timeout 
    duration for your test. If you do not have an explicit SLA, you may set the timeout 
    duration to be some reasonable amount that you would expect the system to complete 
    the process.    
    """

    # set timeout duration to your SLA guarantee
    poll_timeout_duration_secs = 10 
    
    # set a random filename
    test_filename = str(uuid.uuid4()) + ".txt"

    # the file initially contains a lowercase string
    unmodified_message = "this message was created during an integration test"

    # the string will be transformed to uppercase by the end of the process 
    modified_message = "THIS MESSAGE WAS CREATED DURING AN INTEGRATION TEST"

    @classmethod
    def getStackName(cls) -> str:
        stack_name = os.environ.get("AWS_SAM_STACK_NAME")
        if not stack_name:
            raise Exception(
                "Cannot find env var AWS_SAM_STACK_NAME. \n"
                "Please include the stack name when running integration tests."
            )

        return stack_name

    def setUp(self) -> None:
        """
        Based on the provided AWS_SAM_STACK_NAME, we can use CloudFormation API to find out the S3 SourceBucket name
        where the initial data will be put, as well as the DynamoDB TableName where the modified data will eventually reside 
        at the end of the process.
        """
        stack_name = TestAsynchronousTransformation.getStackName()

        client = boto3.client("cloudformation")

        try:
            response = client.describe_stacks(StackName=stack_name)
        except Exception as e:
            raise Exception(
                f"Cannot find stack {stack_name}. \n" f'Please make sure stack with the name "{stack_name}" exists.'
            ) from e

        stacks = response["Stacks"]

        stack_outputs = stacks[0]["Outputs"]
        source_bucket_output = [output for output in stack_outputs if output["OutputKey"] == "SourceBucketName"]
        self.assertTrue(source_bucket_output, f"Cannot find output SourceBucketName in stack {stack_name}")
        self.source_bucket = source_bucket_output[0]["OutputValue"]

        stack_outputs = stacks[0]["Outputs"]
        async_test_results_output = [output for output in stack_outputs if output["OutputKey"] == "AsyncTransformTestResultsTable"]
        self.assertTrue(async_test_results_output, f"Cannot find output AsyncTransformTestResultsTable in stack {stack_name}")
        self.async_test_results_table = async_test_results_output[0]["OutputValue"]

    def testPutObjectIntoSourceBucket(self):
        """
        Put an unmodified, lowercase string into the source bucket. This the is beginning of the async process. 
        """
        print()
        print("Putting unmodified object into S3...")
        client = boto3.client('s3')
        response = client.put_object(Body=self.unmodified_message, Bucket=self.source_bucket, Key=self.test_filename)
        self.assertEqual(response['ResponseMetadata']['HTTPStatusCode'], requests.codes.ok, f"Cannot put object into Source Bucket {self.source_bucket}")

    def testRetrieveObjectFromDynamoDB(self):
        """
        Poll to retrieve the modified string from a DynamoDB Table. This is the end of the async process.
        """    
        print()
        
        # set the maximum amount of time to poll before the test fails
        # this can be based on our system's SLA
        loop_start_time = datetime.now()
        loop_max_time = loop_start_time + timedelta(seconds=self.poll_timeout_duration_secs)

        while True:

            # query dynamodb for the output
            dynamodb = boto3.client("dynamodb")
            response = dynamodb.get_item(
                TableName=self.async_test_results_table,
                Key={
                    'id': {'S': self.test_filename}
                }
            )

            # did we get the object?
            try: 
                x = response['Item']['message']
                print("*** Modified object found in DynamoDB. Success! ***")

                # is the object formed correctly?
                self.assertTrue(x['S'] == self.modified_message, f"Object malformed. Found {x}. Should be: {self.modified_message}")
                
                # if yes, let's get out of here
                break

            except KeyError:
                pass
            
            print("Querying DynamoDB for modified object. Not found yet...")
            
            if (loop_max_time < datetime.now()):
                self.fail("Could not retrieve object from DynamoDB before timeout. Async process failed.")

        # TODO cleanup, make file mods