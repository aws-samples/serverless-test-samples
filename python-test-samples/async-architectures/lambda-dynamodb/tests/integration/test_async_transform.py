# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import uuid
from unittest import TestCase
import time
import boto3
import requests
from datetime import datetime, timedelta

"""
Set the environment variable AWS_SAM_STACK_NAME 
to match the name of the stack you will test
AWS_SAM_STACK_NAME=async-test-pattern python -m pytest -s tests/integration -v
AWS_SAM_STACK_NAME=<stack-name> python -m pytest -s tests/integration -v
"""

class TestAsynchronousTransformation(TestCase):

    poll_timeout_duration_secs = 5 
    test_filename = str(uuid.uuid4()) + ".txt"
    lower_case_message = "this message was created during an integration test"
    upper_case_message = "THIS MESSAGE WAS CREATED DURING AN INTEGRATION TEST"

    @classmethod
    def getStackName(cls) -> str:
        stack_name = os.environ.get("AWS_SAM_STACK_NAME")
        if not stack_name:
            raise Exception(
                "Cannot find env var AWS_SAM_STACK_NAME. \n"
                "Please setup this environment variable with the stack name where we are running integration tests."
            )

        return stack_name

    def setUp(self) -> None:
        """
        Based on the provided env variable AWS_SAM_STACK_NAME,
        here we use CloudFormation API to find out the SourceBucket name 
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
        self.assertTrue(async_test_results_output, f"Cannot find output AsyncTransformTestResults in stack {stack_name}")
        self.async_test_results_table = async_test_results_output[0]["OutputValue"]

    def testPutObjectIntoSourceBucket(self):
        """
        Put an object into the source bucket
        """
        client = boto3.client('s3')
        response = client.put_object(Body=self.lower_case_message, Bucket=self.source_bucket, Key=self.test_filename)
        self.assertEqual(response['ResponseMetadata']['HTTPStatusCode'], requests.codes.ok, f"Cannot put object into Source Bucket {self.source_bucket}")

    def testRetrieveObjectFromDynamoDB(self):
        """
        Poll DynamoDB to retrieve object from end of async process
        """    
        print() # output neatness
        loop_start_time = datetime.now()
        loop_max_time = loop_start_time + timedelta(seconds=self.poll_timeout_duration_secs)

        while True:

            # query dynamodb
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
                print("Queried DynamoDB for object. Success!")

                # is the object formed correctly?
                self.assertTrue(x['S'] == self.upper_case_message, f"Object malformed. Found {x}. Should be: {self.upper_case_message}")
                
                # if yes, let's get out of here
                break

            except KeyError:
                pass
            
            print("Queried DynamoDB for object. Not found yet...")
            
            if (loop_max_time < datetime.now()):
                self.fail("Could not retrieve object from DynamoDB before timeout. Async process failed.")

        # TODO cleanup, make file mods