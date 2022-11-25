# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from os import environ
import json
from datetime import datetime
from unittest import TestCase
from typing import Any, Dict
import yaml
import boto3
from boto3.dynamodb.conditions import Key
import moto

# Import the handler under test
from src import app

# Mock the DynamoDB Service during the test
@moto.mock_dynamodb

class TestSampleLambdaWithDynamoDB(TestCase):
    """
    Unit Test class for src/app.py
    """
    
    def read_sam_template(self, sam_template_fn : str = "template.yaml" ) -> dict:
        """
        Utility Function to read the SAM template for the current project
        """
        with open(sam_template_fn, "r") as fp:
            template =fp.read().replace("!","")   # Ignoring tags
            try:
                return yaml.safe_load(template)
            except yaml.YAMLError as exc:
                    print(exc)

    def load_test_event(self, test_event_file_name: str) ->  Dict[str, Any]:
        """
        Load a sample event from a file
        """
        with open(f"tests/events/{test_event_file_name}.json") as f:
            event = json.load(f)
            # validate(event=event, schema=schemas.INPUT)
            return event

    def setUp(self) -> None:
        """
        Test Set up:
           1. Create the lambda environment variale DYNAMODB_TABLE_NAME
           2. Build a DynamoDB Table according to the SAM template
           3. Populate DynamoDB Data into the Table for test
        """

        # Create a name for a test table, and set the environment
        self.test_ddb_table_name = "unit_test_ddb_table_name"
        environ["DYNAMODB_TABLE_NAME"] = self.test_ddb_table_name 

        # Create a mock table using the definition from the SAM YAML template
        sam_template_table_properties = self.read_sam_template()["Resources"]["DynamoDBTable"]["Properties"]
        self.mock_dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        self.mock_dynamodb_table = self.mock_dynamodb.create_table(
                TableName = self.test_ddb_table_name,
                KeySchema = sam_template_table_properties["KeySchema"],
                AttributeDefinitions = sam_template_table_properties["AttributeDefinitions"],
                BillingMode = sam_template_table_properties["BillingMode"]
                )

        # Populate data for the tests
        self.mock_dynamodb_table.put_item(Item={"PK": "TEST001", 
                                                "SK": "NAME#",
                                                "data": "Unit Test Name Data"})
        
    def tearDown(self) -> None:
        """
        For teardown, remove the mocked table & environment variable
        """
        self.mock_dynamodb_table.delete()
        del environ['DYNAMODB_TABLE_NAME']

    
    def test_lambda_handler_happy_path(self):
        """
        Happy path test where the id name record exists in the DynamoDB Table

        Since the environment variable DYNAMODB_TABLE_NAME is set 
        and DynamoDB is mocked for the entire class, this test will 
        implicitly use the mocked DynamoDB table we created in setUp.
        """

        test_event = self.load_test_event("sampleEvent_Found_TEST001")
        test_return = app.lambda_handler(event=test_event,context=None)
        self.assertEqual( test_return["statusCode"] , 200)
        self.assertEqual( test_return["body"] , "Hello Unit Test Name Data!")

        # Verify the log entries

        id_items = self.mock_dynamodb_table.query(
            KeyConditionExpression=Key('PK').eq('TEST001')
        )
    
        # Log entry item to the original name item
        self.assertEqual( len(id_items["Items"]) , 2)

        # Check the log entry item
        for item in id_items["Items"]:
            if item["SK"] != "NAME#":
                self.assertEqual( item["data"] , "Hello Unit Test Name Data!")
                self.assertEqual( item["SK"][0:11] , "DT#" + datetime.now().strftime("%Y%m%d"))
        

    def test_lambda_handler_notfound_path(self):
        """
        Unhappy path test where the id name record does not exist in the DynamoDB Table
        """

        test_event = self.load_test_event("sampleEvent_NotFound_TEST002")
        test_return = app.lambda_handler(event=test_event,context=None)
        self.assertEqual( test_return["statusCode"] , 404)
        self.assertEqual( test_return["body"] , "NOTFOUND: Name Not Found for ID TEST002")

        # Verify the log entries

        id_items = self.mock_dynamodb_table.query(
            KeyConditionExpression=Key('PK').eq('TEST002')
        )
    
        # Log entry item to the original name item
        self.assertEqual(len(id_items["Items"]), 1)

        # Check the log entry item
        for item in id_items["Items"]:
            self.assertEqual(item["data"], "NOTFOUND: Name Not Found for ID TEST002")
            self.assertEqual(item["SK"][0:11], "DT#" + datetime.now().strftime("%Y%m%d"))
        

    