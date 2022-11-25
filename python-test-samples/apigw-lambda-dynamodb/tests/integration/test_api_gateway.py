# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
from unittest import TestCase
from boto3.dynamodb.conditions import Key
import boto3
import requests

"""
Set the environment variable AWS_SAM_STACK_NAME 
to match the name of the stack you will test

AWS_SAM_STACK_NAME=<stack-name> python -m pytest -s tests/integration -v
"""

class TestApiGateway(TestCase):
    api_endpoint: str

    @classmethod
    def get_stack_name(cls) -> str:
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
        We use the cloudformation API to retrieve the HelloPersonApi URL and the DynamoDB Table Name
        We also seed the DynamoDB Table for the test
        """
        stack_name = TestApiGateway.get_stack_name()

        client = boto3.client("cloudformation")

        try:
            response = client.describe_stacks(StackName=stack_name)
        except Exception as e:
            raise Exception(
                f"Cannot find stack {stack_name}. \n" f'Please make sure stack with the name "{stack_name}" exists.'
            ) from e

        # HelloPersonApi
        stack_outputs = response["Stacks"][0]["Outputs"]
        api_outputs = [output for output in stack_outputs if output["OutputKey"] == "HelloPersonApi"]
        self.assertTrue(api_outputs, f"Cannot find output HelloPersonApi in stack {stack_name}")
        self.api_endpoint = api_outputs[0]["OutputValue"]

        # DynamoDBTableName
        dynamodb_outputs = [output for output in stack_outputs if output["OutputKey"] == "DynamoDBTableName"]
        self.assertTrue(dynamodb_outputs, f"Cannot find output DynamoDBTableName in stack {stack_name}")
        self.dynamodb_table_name = dynamodb_outputs[0]["OutputValue"] 

        # Seed the DynamoDB Table with Test Data
        dynamodb_resource = boto3.resource("dynamodb", region_name="us-east-1")
        dynamodb_table = dynamodb_resource.Table(name=self.dynamodb_table_name)
        dynamodb_table.put_item(Item={"PK": "TEST001", 
                                            "SK": "NAME#",
                                            "data": "Unit Test Name Data"})


    def tearDown(self) -> None:
        """
        # For tear-down, remove any data injected for the tests
        # Table particular care to ensure these values are unique and identifiable as TEST data.
        """
        dynamodb_resource = boto3.resource("dynamodb", region_name="us-east-1")
        dynamodb_table = dynamodb_resource.Table(name=self.dynamodb_table_name)

        for id in ["TEST001","TEST002"]:
            id_items = dynamodb_table.query(
                KeyConditionExpression=Key('PK').eq(id)
            )
            if "Items" in id_items:
                for item in id_items["Items"]:
                    dynamodb_table.delete_item(Key={"PK":item["PK"],"SK":item["SK"]})

    def test_api_gateway_200(self):
        """
        Call the API Gateway endpoint and check the response for a 200
        """
        response = requests.get(self.api_endpoint.replace("{id}","TEST001"))
        self.assertEqual(response.status_code, requests.codes.ok)

    def test_api_gateway_404(self):
        """
        Call the API Gateway endpoint and check the response for a 404 (id not found)
        """    
        response = requests.get(self.api_endpoint.replace("{id}","TEST002"))
        self.assertEqual(response.status_code, requests.codes.not_found)
