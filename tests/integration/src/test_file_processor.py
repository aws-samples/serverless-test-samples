# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
from time import sleep
from unittest import TestCase
from uuid import uuid4
import boto3
import requests
import json
from boto3.dynamodb.conditions import Key


"""
Set the environment variable AWS_SAM_STACK_NAME 
to match the name of the stack you will test

AWS_SAM_STACK_NAME=<stack-name> python -m pytest -s tests/integration -v
"""

class TestFileProcessingWorkflow(TestCase):
    """
    Test case for the file processing workflow
    """
    api_endpoint: str
    aws_region = os.environ.get("AWS_DEFAULT_REGION") or "us-east-1"

    @classmethod
    def get_stack_name(cls) -> str:
        stack_name = os.environ.get("AWS_SAM_STACK_NAME")
        if not stack_name:
            raise Exception(
                "Cannot find env var AWS_SAM_STACK_NAME. \n" 
                "Please setup this environment variable with the stack name where we are running integration tests. \n"
                "AWS_SAM_STACK_NAME=<stack-name> python -m pytest -s tests/integration -v"
            )

        return stack_name

    def setUp(self) -> None:
        """
        Based on the provided env variable AWS_SAM_STACK_NAME,
        We use the cloudformation API to retrieve the GetInventory URL and the DynamoDB Table Name
        We also seed the DynamoDB Table for the test
        """
        stack_name = TestFileProcessingWorkflow.get_stack_name()

        client = boto3.client("cloudformation")

        try:
            response = client.describe_stacks(StackName=stack_name)
        except Exception as e:
            raise Exception(
                f"Cannot find stack {stack_name}. \n" f'Please make sure stack with the name "{stack_name}" exists.'
            ) from e

        # locationsApi
        stack_outputs = response["Stacks"][0]["Outputs"]
        api_outputs = [output for output in stack_outputs if output["OutputKey"] == "ApiEndpoint"]
        self.assertTrue(api_outputs, f"Cannot find output locations in stack {stack_name}")
        self.api_endpoint = api_outputs[0]["OutputValue"]

        # DynamoDBTableName
        dynamodb_outputs = [output for output in stack_outputs if output["OutputKey"] == "DynamoDBTableName"]
        self.assertTrue(dynamodb_outputs, f"Cannot find output DynamoDBTableName in stack {stack_name}")
        self.dynamodb_table_name = dynamodb_outputs[0]["OutputValue"] 

        # UnicornInventoryBucket
        inv_bucket_outputs = [output for output in stack_outputs if output["OutputKey"] == "UnicornInventoryBucket"]
        self.assertTrue(inv_bucket_outputs, f"Cannot find output UnicornInventoryBucket in stack {stack_name}")
        self.inv_bucket_name = inv_bucket_outputs[0]["OutputValue"] 

        # Create a random postfix for the id's to prevent data collisions between tests
        # Using unique id's per unit test will isolate test data
        # Use this id in all test data values or artifacts

        self.id_postfix = "_" + str(uuid4())
        self.test_unicorn = f"TEST_UNI{self.id_postfix}"
        self.test_location = f"TEST_LOC{self.id_postfix}"

    def tearDown(self) -> None:
        """
        # For tear-down, remove any data injected for the tests
        # Take particular care to ensure these values are unique and identifiable as TEST data.
        """
        dynamodb_resource = boto3.resource("dynamodb", region_name = self.aws_region)
        dynamodb_table = dynamodb_resource.Table(name=self.dynamodb_table_name)

        id_items = dynamodb_table.query(
            KeyConditionExpression=Key('PK').eq(self.test_unicorn)
        )
        if "Items" in id_items:
            for item in id_items["Items"]:
                dynamodb_table.delete_item(Key={"PK":self.test_unicorn})

        # And fix the locations
        location_list_q = dynamodb_table.get_item(
        Key={
            'PK': "LOCATION#LIST"
            }
        )
        if "Item" in location_list_q:
            locations = [ x for x in location_list_q["Item"]["LOCATIONS"] if x != self.test_location ]
            response = dynamodb_table.put_item(
                Item={
                    'PK': "LOCATION#LIST",
                    'LOCATIONS': locations
                }
            )

    def test_file_processor_happy_path(self):
        """
        Test that given an S3 file, the Unicorn is created in DynamoDB
        In a real-world scenario, we would test variations and failure modes as well
        """

        print(f"\nTest Data: {self.test_unicorn}\n")

        dynamodb_resource = boto3.resource("dynamodb", region_name = self.aws_region)
        dynamodb_table = dynamodb_resource.Table(name=self.dynamodb_table_name)

        # Verify the data is not there, which would invalidate the test
        item_should_not_be_found = dynamodb_table.query(
            KeyConditionExpression=Key('PK').eq(self.test_unicorn)
        )
        self.assertEqual(item_should_not_be_found["Count"], 0, "Data exists before test, invalid starting state")

        # Seed the S3 Bucket with Test Data
        # Note the uniqueness of the test data and S3 key to prevent collisions with actual data:
        #    both the postfix and the exact test name are part of the filename.
        test_data_csv = f'"Unicorn Name","Unicorn Location"\n"{self.test_unicorn}","{self.test_location}"\n'
        test_data_save_key = f"INTEGRATION_TEST/TEST{self.id_postfix}.test_file_processor_happy_path.csv"
        s3_client = boto3.client('s3')
        s3_client.put_object(Body=test_data_csv,
                            Bucket=self.inv_bucket_name, 
                            Key=test_data_save_key)
        
        # Poll for processing completion
        poll_max_seconds = 30
        poll_complete_seconds = 0

        while poll_complete_seconds < poll_max_seconds:
            # Check that data is present
            item_should_be_found = dynamodb_table.query(
                KeyConditionExpression=Key('PK').eq(self.test_unicorn)
            )
            if item_should_be_found["Count"] == 0:
                sleep(1)
                poll_complete_seconds +=1
            else:
                break

        # Happy Path Checks: 1 item found within a good timeframe, data is as expected.
        self.assertGreater(item_should_be_found["Count"], 0, "Item not found after time allowed for processing.")
        self.assertLessEqual(poll_complete_seconds, 2, f"Item took too long for processing: {poll_complete_seconds} sec")
        self.assertEqual(item_should_be_found["Count"], 1, "More than one item found after insert of data")
        self.assertEqual(item_should_be_found["Items"][0]["PK"], self.test_unicorn, 
                         "Table PK is not set to the Unicorn Name: " + \
                         item_should_be_found["Items"][0]["PK"] + " expected " + self.test_unicorn)
        self.assertEqual(item_should_be_found["Items"][0]["LOCATION"], self.test_location, 
                         "Table LOCATION is not set to the Unicorn Location: " + \
                         item_should_be_found["Items"][0]["LOCATION"] + " expected " + self.test_location)
        self.assertIn(item_should_be_found["Items"][0]["STATUS"],["IN_TRAINING","AVAILABLE"],
                      "Table STATUS is not valid")

