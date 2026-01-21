"""
Unit Test 
"""
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from decimal import Decimal
from os import environ
import json
from unittest import TestCase
from typing import Any, Dict
import yaml
import boto3
import moto


# Import the handler under test
from src import app

# Mock the DynamoDB Service during the test
@moto.mock_dynamodb

class TestSampleLambdaWithDynamoDB(TestCase):
    """
    Unit Test class for src/app.py
    """

    def setUp(self) -> None:
        """
        Test Set up:
           1. Create the lambda environment variable STOCKS_DB_TABLE and CURRENCIES_DB_TABLE
           2. Build DynamoDB Tables according to the SAM template
           4. Populate DynamoDB Data into the Tables for test
        """

        # Create a name for a test table, and set the environment
        self.test_stocks_table_name = "unit_test_stock_table_name"
        environ["STOCKS_DB_TABLE"] = self.test_stocks_table_name

        # Create a mock table using the definition from the SAM YAML template
        # This simple technique works if there are no intrinsics (like !If or !Ref) in the
        # resource properties for KeySchema, AttributeDefinitions, & BillingMode.
        sam_template_table_properties = \
            self.read_sam_template()["Resources"]["StocksTable"]["Properties"]
        self.mock_dynamodb = boto3.resource("dynamodb")
        self.mock_dynamodb_table = self.mock_dynamodb.create_table(
            TableName = self.test_stocks_table_name,
            KeySchema = sam_template_table_properties["KeySchema"],
            AttributeDefinitions = sam_template_table_properties["AttributeDefinitions"],
            BillingMode = sam_template_table_properties["BillingMode"]
        )

        # Populate data for the tests
        self.mock_dynamodb_table.put_item(Item={
                                                "STOCK_ID": "1", 
                                                "Value": 3})

        # Create a name for a test table, and set the environment
        self.test_currencies_table_name = "unit_test_currencies_table_name"
        environ["CURRENCIES_DB_TABLE"] = self.test_currencies_table_name

        # Create a mock table using the definition from the SAM YAML template
        # This simple technique works if there are no intrinsics (like !If or !Ref) in the
        # resource properties for KeySchema, AttributeDefinitions, & BillingMode.
        sam_template_table_properties = \
            self.read_sam_template()["Resources"]["CurrenciesTable"]["Properties"]
        self.mock_dynamodb = boto3.resource("dynamodb")
        self.mock_currencies_table = self.mock_dynamodb.create_table(
            TableName = self.test_currencies_table_name,
            KeySchema = sam_template_table_properties["KeySchema"],
            AttributeDefinitions = sam_template_table_properties["AttributeDefinitions"],
            BillingMode = sam_template_table_properties["BillingMode"]
        )

        # Populate data for the tests
        self.mock_currencies_table.put_item(Item={
                                                "CURRENCY": "USD", 
                                                "Rate": Decimal("1.31")})
        self.mock_currencies_table.put_item(Item={
                                                "CURRENCY": "CAD", 
                                                "Rate": Decimal("1.41")})
        self.mock_currencies_table.put_item(Item={
                                                "CURRENCY": "AUD", 
                                                "Rate": Decimal("1.51")})
    def tearDown(self) -> None:
        """
        For teardown, remove the mocked table & environment variable
        """
        self.mock_dynamodb_table.delete()
        del environ['STOCKS_DB_TABLE']

    def read_sam_template(self, sam_template_fn : str = "template.yaml" ) -> dict:
        """
        Utility Function to read the SAM template for the current project
        """
        with open(sam_template_fn, "r",encoding="utf-8") as fptr:
            template =fptr.read().replace("!","")   # Ignoring intrinsic tags
            return yaml.safe_load(template)

    def load_test_event(self, test_event_file_name: str) ->  Dict[str, Any]:
        """
        Load a sample event from a file
        """
        with open(f"tests/events/{test_event_file_name}.json","r",encoding="utf-8") as fptr:
            event = json.load(fptr)
            return event


    def test_lambda_handler_happy_path(self):
        """
        Happy path test where the stock ID exists in the DynamoDB Table

        Since the environment variable STOCKS_DB_TABLE and CURRENCIES_DB_TABLE
        are set and DynamoDB is mocked for the entire class, this test will 
        implicitly use the mocked DynamoDB table we created in setUp.
        """

        test_event = self.load_test_event("testevent")
        test_return = app.lambda_handler(event=test_event,context=None)
        self.assertEqual( test_return["statusCode"] , 200)
        expected = '{"message": {"stock": "1", "values": {"EUR": 3.0, "USD": 3.93, "CAD": 4.23, "AUD": 4.53}}}'
        self.assertEqual( test_return["body"] , expected)

    def test_lambda_handler_failure(self):
        """
        Failure Test where the stock ID does not exist in the DynamoDB Table

        Since the environment variable STOCKS_DB_TABLE and CURRENCIES_DB_TABLE
        are set and DynamoDB is mocked for the entire class, this test will 
        implicitly use the mocked DynamoDB table we created in setUp.
        """

        test_event = self.load_test_event("testevent-failure")
        test_return = app.lambda_handler(event=test_event,context=None)
        self.assertEqual( test_return["statusCode"] , 404)
        self.assertEqual( test_return["body"], "Stock not found")
