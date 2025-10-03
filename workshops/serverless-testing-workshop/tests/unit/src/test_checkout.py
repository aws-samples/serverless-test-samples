"""
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# Start of unit test code for /src/Checkout/app.py
"""

import sys
from os import environ
import json
from datetime import datetime
from unittest import TestCase
from typing import Any, Dict
from uuid import uuid4
import yaml
import boto3
from boto3.dynamodb.conditions import Key
import moto
from aws_xray_sdk.core import xray_recorder
xray_recorder.begin_segment("Mock Segment")

sys.path.insert(0,'./src/Checkout')
print(sys.path)

from schemas import OUTPUT_SCHEMA                     # pylint: disable=wrong-import-position

# Import the handler under test
import app

# Mock all AWS Services 
@moto.mock_aws


class TestSampleLambdaWithDynamoDB(TestCase):
    
    def setUp(self) -> None:
        """
        Test Set up:
           1. Create the Lambda environment variable DYNAMODB_TABLE_NAME
           2. Build a DynamoDB Table according to the SAM template
           3. Populate DynamoDB Data into the Table for test
        """

        #
        self.LAMBDA_TASK_ROOT = "LAMBDA_TASK_ROOT"
        environ["LAMBDA_TASK_ROOT_KEY"] = self.LAMBDA_TASK_ROOT

        self._X_AMZN_TRACE_ID = "_X_AMZN_TRACE_ID"
        environ["LAMBDA_TRACE_HEADER_KEY"] = self._X_AMZN_TRACE_ID

        # Create a name for a test table, and set the environment
        self.test_ddb_table_name = "unit_test_ddb_table_name"
        environ["DYNAMODB_TABLE_NAME"] = self.test_ddb_table_name 

        # Create a mock table using the definition from the SAM YAML template
        # This simple technique works if there are no intrinsics (like !If or !Ref) in the
        # resource properties for KeySchema, AttributeDefinitions, & BillingMode.
        sam_template_table_properties = self.read_sam_template()["Resources"]["UnicornInventoryTable"]["Properties"]

        print(f"Creating mock DynamoDB Table: {self.test_ddb_table_name}")

        self.mock_dynamodb = boto3.resource("dynamodb")
        self.mock_dynamodb_table = self.mock_dynamodb.create_table(
                TableName = self.test_ddb_table_name,
                KeySchema=[{"AttributeName": "PK", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "PK", "AttributeType": "S"}],
                # KeySchema = sam_template_table_properties["KeySchema"],
                # AttributeDefinitions = sam_template_table_properties["AttributeDefinitions"],
                # BillingMode = sam_template_table_properties["BillingMode"]
                BillingMode = "PAY_PER_REQUEST"
                )
   
        print(f"Created mock DynamoDB Table: {self.test_ddb_table_name}")

        # Populate doctype and customername data for the tests
        self.mock_dynamodb_table.put_item(Item={"PK": "TESTUNICORN",
                                                 "LOCATION": "US",
                                                 "STATUS": "AVAILABLE",
                                                 })
        self.mock_dynamodb_table.put_item(Item={"PK": "TESTUNICORN2",
                                                 "LOCATION": "US",
                                                 "STATUS": "AVAILABLE",
                                                 })

    def read_sam_template(self, sam_template_fn : str = "template.yaml" ) -> dict:
        """
        Utility Function to read the SAM template for the current project
        """
        with open(sam_template_fn, "r") as fp:
            template =fp.read().replace("!","")   # Ignoring intrinsic tags
            return yaml.safe_load(template)

    def load_test_event(self, test_event_file_name: str) ->  Dict[str, Any]:
        """
        Load a sample event from a file
        Add the test isolation postfix to the path parameter {id}
        """
        with open(f"tests/events/{test_event_file_name}.json","r") as f:
            event = json.load(f)
            # event["pathParameters"]["id"] = event["pathParameters"]["id"] + self.id_postfix
            return event
    
    def test_lambda_handler_happy_path(self):
        """
        Happy path test where the id name record exists in the DynamoDB Table

        Since the environment variable DYNAMODB_TABLE_NAME is set 
        and DynamoDB is mocked for the entire class, this test will 
        implicitly use the mocked DynamoDB table we created in setUp.
        """
        print("test happy path-----------")

        test_event = self.load_test_event("sampleEvent")
        print(f"TEST EVENT: {test_event}")
        
        test_return = app.lambda_handler(event=test_event,context=None)
        print(f"TEST RETURN: {test_return}")
        
        self.assertEqual(test_return["statusCode"] , 200)
        self.assertEqual(test_return["body"] , "OK")

        # Verify the log entries
        id_items = self.mock_dynamodb_table.query(
            KeyConditionExpression=Key('PK').eq('TESTUNICORN')
        )

        # Check the log entry item
        for item in id_items["Items"]:
            self.assertEqual( item["PK"] , "TESTUNICORN")
            self.assertEqual( item["STATUS"], "RESERVED")
 
    def test_lambda_handler_not_that_happy_path(self):
        
            """
            This is not the happy path

            Since the environment variable DYNAMODB_TABLE_NAME is set 
            and DynamoDB is mocked for the entire class, this test will 
            implicitly use the mocked DynamoDB table we created in setUp.
            Check the test_lambda_handler_happy_path, what is the difference with this assertion?
            """
            test_event = self.load_test_event("sampleEvent")
            print(f"TEST EVENT: {test_event}")
            
            test_return = app.lambda_handler(event=test_event,context=None)
            print(f"TEST RETURN: {test_return}")
            
            self.assertEqual(test_return["statusCode"] , 200)
            self.assertEqual(test_return["body"] , "OK")

            # Verify the log entries
            id_items = self.mock_dynamodb_table.query(
                KeyConditionExpression=Key('PK').eq('TESTUNICORN2')
            )
            # TIP! We didn't reserve this unicorn....
            # Check the log entry item
            for item in id_items["Items"]:
                self.assertEqual( item["PK"] , "TESTUNICORN2")
                self.assertEqual( item["STATUS"], "RESERVED")
      
    def tearDown(self) -> None:
        """
        For teardown, remove the mocked table & environment variable
        """
        self.mock_dynamodb_table.delete()
        del environ['DYNAMODB_TABLE_NAME']
