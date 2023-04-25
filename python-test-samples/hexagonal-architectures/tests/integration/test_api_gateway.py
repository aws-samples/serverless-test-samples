# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
from decimal import Decimal
from unittest import TestCase
from uuid import uuid4
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

    aws_region = os.environ.get("AWS_DEFAULT_REGION") or "us-east-1"

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
        We use the cloudformation API to retrieve the StockConverterApi URL and the DynamoDB Table Name
        We also seed the DynamoDB Table for the test
        """
        stack_name = TestApiGateway.get_stack_name()

        client = boto3.client("cloudformation")
        print(stack_name)
        try:
            response = client.describe_stacks(StackName=stack_name)
        except Exception as e:
            raise Exception(
                f"Cannot find stack {stack_name}. \n" f'Please make sure stack with the name "{stack_name}" exists.'
            ) from e

        # StockConverterApi
        print(stack_name, response)
        stack_outputs = response["Stacks"][0]["Outputs"]
        api_outputs = [output for output in stack_outputs if output["OutputKey"] == "StockConverterApi"]
        self.assertTrue(api_outputs, f"Cannot find output StockConverterApi in stack {stack_name}")
        self.api_endpoint = api_outputs[0]["OutputValue"]

        # CurrenciesTableName
        currencies_dynamodb_outputs = [output for output in stack_outputs if output["OutputKey"] == "CurrenciesTableName"]
        self.assertTrue(currencies_dynamodb_outputs, f"Cannot find output DynamoDBTableName in stack {stack_name}")
        self.currencies_dynamodb_table_name = currencies_dynamodb_outputs[0]["OutputValue"] 

        # Seed the Currencies DynamoDB Table with Test Data
        dynamodb_resource = boto3.resource("dynamodb", region_name = self.aws_region)
        currencies_dynamodb_table = dynamodb_resource.Table(name=self.currencies_dynamodb_table_name)
        currencies_dynamodb_table.put_item(Item={"CURRENCY": "USD", 
                                      "Rate": Decimal("1.31")})
        currencies_dynamodb_table.put_item(Item={"CURRENCY": "CAD", 
                                      "Rate": Decimal("1.41")})
        currencies_dynamodb_table.put_item(Item={"CURRENCY": "AUD", 
                                      "Rate": Decimal("1.51")})

        # StocksTableName
        stocks_dynamodb_outputs = [output for output in stack_outputs if output["OutputKey"] == "StocksTableName"]
        self.assertTrue(stocks_dynamodb_outputs, f"Cannot find output DynamoDBTableName in stack {stack_name}")
        self.stocks_dynamodb_table_name = stocks_dynamodb_outputs[0]["OutputValue"] 

        # Seed the Currencies DynamoDB Table with Test Data
        dynamodb_resource = boto3.resource("dynamodb", region_name = self.aws_region)
        stocks_dynamodb_table = dynamodb_resource.Table(name=self.stocks_dynamodb_table_name)
        stocks_dynamodb_table.put_item(Item={"STOCK_ID": "1", 
                                      "Value": 3})


    def tearDown(self) -> None:
        """
        # For tear-down, remove any data injected for the tests
        """
        dynamodb_resource = boto3.resource("dynamodb", region_name = self.aws_region)
        currencies_dynamodb_table = dynamodb_resource.Table(name=self.currencies_dynamodb_table_name)

        for id in ["AUD", "USD", "CAD"]:
            currencies_dynamodb_table.delete_item(Key={"CURRENCY":id})

        stocks_dynamodb_table = dynamodb_resource.Table(name=self.stocks_dynamodb_table_name)
        stocks_dynamodb_table.delete_item(Key={"STOCK_ID":"1"})

    def test_api_gateway_200(self):
        """
        Call the API Gateway endpoint and check the response for a 200
        """
        print(self.api_endpoint)
        print("URL", self.api_endpoint.replace("{stock_id}","1"))
        response = requests.get(self.api_endpoint.replace("{stock_id}","1"))
        self.assertEqual(response.status_code, requests.codes.ok)

    def test_api_gateway_404(self):
        """
        Call the API Gateway endpoint and check the response for a 404 (id not found)
        """    
        response = requests.get(self.api_endpoint.replace("{stock_id}","2"))
        self.assertEqual(response.status_code, requests.codes.not_found)