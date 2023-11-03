"""
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""

import os
import json
from unittest import TestCase
from uuid import uuid4
import requests
import boto3


class TestLocations(TestCase):
    """
    Test the Locations Endpoint functionality
    Set the environment variable AWS_SAM_STACK_NAME 
    to match the name of the stack you will test

    AWS_SAM_STACK_NAME=<stack-name> python -m pytest -s tests/integration -v
    """
    api_endpoint: str

    aws_region = os.environ.get("AWS_DEFAULT_REGION") or "us-east-1"

    @classmethod
    def get_stack_name(cls) -> str:
        """
        Retrieve the SUT stack name from an environment variable AWS_SAM_STACK_NAME
        Fail test if not found
        """
        stack_name = os.environ.get("AWS_SAM_STACK_NAME")
        if not stack_name:
            raise Exception(
                "Cannot find env var AWS_SAM_STACK_NAME. \n"
                "Please setup this environment variable with the stack name for integration tests."
            )

        return stack_name

    def setUp(self) -> None:
        """
        Based on the provided env variable AWS_SAM_STACK_NAME,
        We use the cloudformation API to retrieve the GetInventory URL and the DynamoDB Table Name
        We also seed the DynamoDB Table for the test
        """
        stack_name = TestLocations.get_stack_name()

        client = boto3.client("cloudformation")

        try:
            response = client.describe_stacks(StackName=stack_name)
        except Exception as e:
            raise Exception(
                f"Cannot find stack {stack_name}. \n"  + \
                f'Please make sure stack with the name "{stack_name}" exists.'
            ) from e

        stack_outputs = response["Stacks"][0]["Outputs"]

        # Locations Api Endpoint
        api_outputs = [output for output in stack_outputs if output["OutputKey"] == "ApiEndpoint"]
        self.assertTrue(api_outputs, f"Cannot find output locations in {stack_name}")
        self.api_endpoint = api_outputs[0]["OutputValue"]

        # DynamoDBTableName
        dynamodb_outputs = [output for output in stack_outputs
                            if output["OutputKey"] == "DynamoDBTableName"]
        self.assertTrue(dynamodb_outputs, f"Cannot find output DynamoDBTableName in {stack_name}")
        self.dynamodb_table_name = dynamodb_outputs[0]["OutputValue"]

        # Create a random postfix for the id's to prevent data collisions between tests
        # Using unique id's per unit test will isolate test data
        # Use this id in all test data values or artifacts

        self.id_postfix = "_" + str(uuid4())
        self.test_location = f"TEST_LOC{self.id_postfix}"

        # Seed the DynamoDB Table with Test Data - add it to the existing locations
        dynamodb_resource = boto3.resource("dynamodb", region_name = self.aws_region)
        dynamodb_table = dynamodb_resource.Table(name=self.dynamodb_table_name)

        location_list_q = dynamodb_table.get_item(
        Key={
            'PK': "LOCATION#LIST"
            }
        )
        if "Item" in location_list_q:
            locations = location_list_q["Item"]["LOCATIONS"]
            locations.append(self.test_location)
        else:
            locations = [self.test_location]

        response = dynamodb_table.put_item(
                Item={
                    'PK': "LOCATION#LIST",
                    'LOCATIONS': locations
                })

    def tearDown(self) -> None:
        """
        # For tear-down, remove any data injected for the tests
        # Take particular care to ensure these values are unique and identifiable as TEST data.
        """
        dynamodb_resource = boto3.resource("dynamodb", region_name = self.aws_region)
        dynamodb_table = dynamodb_resource.Table(name=self.dynamodb_table_name)

        # Remove the test locations from the locations list
        location_list_q = dynamodb_table.get_item(
        Key={
            'PK': "LOCATION#LIST"
            }
        )
        if "Item" in location_list_q:
            locations = [ x for x in location_list_q["Item"]["LOCATIONS"]
                         if x != self.test_location ]
            _ = dynamodb_table.put_item(
                Item={
                    'PK': "LOCATION#LIST",
                    'LOCATIONS': locations
                }
            )

    def test_api_gateway_200(self):
        """
        Call the API Gateway endpoint and check the response for a 200
        """
        response = requests.get(self.api_endpoint + '/locations')
        self.assertEqual(response.status_code, requests.codes.ok)

    def test_locations_response(self):
        """""
        this response have a country that doesn't exists in the api response
        you will have to fix this test!
        """
        response = requests.get(self.api_endpoint + '/locations')
        response_json=json.loads(response.content.decode('ASCII'))

        # Hmm this does not seem to be working, is it the test?
        print(response_json)
        location_exists= "SOME_LOCATION" in response_json["locations"]
        self.assertTrue(location_exists)


    def test_api_gateway_404(self):
        """
        Call the API Gateway endpoint and check the response for a 404 (id not found)
        """
        response = requests.get(self.api_endpoint + 'incorrectxxlocationsxxincorrect')
        response_json=json.loads(response.content.decode('ASCII'))
        self.assertEqual(response_json["message"], "Missing Authentication Token")
