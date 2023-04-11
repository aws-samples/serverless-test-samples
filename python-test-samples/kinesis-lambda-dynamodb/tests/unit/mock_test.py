# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import json
from datetime import datetime
from unittest import TestCase
from typing import Any, Dict
from uuid import uuid4
import yaml
import boto3
from boto3 import Session
from boto3.dynamodb.conditions import Key
import moto
#from moto import mock_dynamodb2


# Import the handler under test
#from src.app import lambda_handler

# Mock the DynamoDB Service during the test
@moto.mock_dynamodb
class TestKinesisLambdaWithDynamoDB(TestCase):
    """
    Unit Test class for src/app.py
    """
    
    
    def setUp(self) -> None:
        """
        Test Set up:
           1. Create the lambda environment variale DYNAMODB_TABLE_NAME
           2. Mock Writes to DynamoDB batch writes
           3. Create a random postfix for this test instance to prevent data collisions
           4. Populate DynamoDB Data into the Table for test
        """

        # Create a name for a test table, and set the environment
        self.test_ddb_table_name = "unit_test_table_name"
        os.environ["DYNAMODB_TABLE_NAME"] = self.test_ddb_table_name
        sam_template_table_properties = self.read_sam_template()["Resources"]["DynamoDBTable"]["Properties"]
        self.mock_dynamodb = boto3.Session(region_name="us-east-1").resource("dynamodb")
        self.mock_dynamodb_table = self.mock_dynamodb.create_table(
                TableName = self.test_ddb_table_name,
                KeySchema = sam_template_table_properties["KeySchema"],
                AttributeDefinitions = sam_template_table_properties["AttributeDefinitions"],
                BillingMode = sam_template_table_properties["BillingMode"]
                )
        
        
    def tearDown(self) -> None:
        """
        For teardown, remove the environment variable
        """
        
        del os.environ['DYNAMODB_TABLE_NAME']

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
        try:
            
            with open(f"{test_event_file_name}.json","r") as f:
                event = json.load(f)
                return event
        except json.decoder.JSONDecodeError:
            print("Invalid JSON data", event)
    
    def test_lambda_handler_happy_path(self):
        """
        Happy path test where the id name record exists in the DynamoDB Table

        Since the environment variable DYNAMODB_TABLE_NAME is set 
        and DynamoDB is mocked for the entire class, this test will 
        implicitly use the mocked DynamoDB table we created in setUp.
        """

        test_event = self.load_test_event("sample_test_event")
        from src.app import lambda_handler
        test_return = lambda_handler(event=test_event,context=None)
        

        self.assertEqual( test_return["statusCode"] , 200)
        self.assertEqual( test_return["body"] , "Kinesis events processed and persisted to DynamoDB table")