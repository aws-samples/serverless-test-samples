# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from os import environ
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
from moto import mock_dynamodb2


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
           1. Create the lambda environment variale DYNAMODB_TABLE_NAME
           2. Mock Writes to DynamoDB batch writes
           3. Create a random postfix for this test instance to prevent data collisions
           4. Populate DynamoDB Data into the Table for test
        """

        # Create a name for a test table, and set the environment
        self.test_ddb_table_name = "unit_test_ddb_table_name"
        environ["DYNAMODB_TABLE_NAME"] = self.test_ddb_table_name 

        
        
    def tearDown(self) -> None:
        """
        For teardown, remove the environment variable
        """
        
        del environ['DYNAMODB_TABLE_NAME']

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
            return event

    
    def test_lambda_handler_happy_path(self):
        """
        Happy path test where the id name record exists in the DynamoDB Table

        Since the environment variable DYNAMODB_TABLE_NAME is set 
        and DynamoDB is mocked for the entire class, this test will 
        implicitly use the mocked DynamoDB table we created in setUp.
        """

        test_event = self.load_test_event("sample_test_event")
        test_return = app.lambda_handler(event=test_event,context=None)
        with mock_dynamodb2():
          ddb_mock = Session().client("dynamodb")
          ddb_mock.batch_write_items(
              RequestItems={
            "unit_test_table_name": [
                {
                    "PutRequest": {
                        "Item": {
                            "PK": {"S": "e04c537a-7177-4254-afae-594470849a2d"},
                            "SK": {"S": "0537f1b4-e439-4ed0-ab09-f327f05550ac"},
                        }
                    }
                },
                {
                    "PutRequest": {
                        "Item": {
                            "PK": {"S": "e04c537a-7177-4254-afae-594470849a2d"},
                            "SK": {"S": "2734e753-6330-4658-b0d7-a9bcde4fd3a5"},
                        }
                    }
                },
                {
                    "PutRequest": {
                        "Item": {
                            "PK": {"S": "e04c537a-7177-4254-afae-594470849a2d"},
                            "SK": {"S": "369c296e-5b15-4503-99c4-fd469e61bd4c"},
                        }
                    }
                },
                {
                    "PutRequest": {
                        "Item": {
                            "PK": {"S": "e04c537a-7177-4254-afae-594470849a2d"},
                            "SK": {"S": "85a05bd1-147a-4872-a830-cb6c7e229e08"},
                        }
                    }
                },
                {
                    "PutRequest": {
                        "Item": {
                            "PK": {"S": "e04c537a-7177-4254-afae-594470849a2d"},
                            "SK": {"S": "d3f475d5-301c-4482-9614-2b18d45b5a45"},
                        }
                    }
                }
            ]
        }
        )
          assert ddb_mock.mock_calls == [
            ddb_mock.call("batch_write_item", RequestItems={"unit_test_table_name": [
            {
                    "PutRequest": {
                        "Item": {
                            "PK": {"S": "e04c537a-7177-4254-afae-594470849a2d"},
                            "SK": {"S": "0537f1b4-e439-4ed0-ab09-f327f05550ac"},
                        }
                    }
                },
                {
                    "PutRequest": {
                        "Item": {
                            "PK": {"S": "e04c537a-7177-4254-afae-594470849a2d"},
                            "SK": {"S": "2734e753-6330-4658-b0d7-a9bcde4fd3a5"},
                        }
                    }
                },
                {
                    "PutRequest": {
                        "Item": {
                            "PK": {"S": "e04c537a-7177-4254-afae-594470849a2d"},
                            "SK": {"S": "369c296e-5b15-4503-99c4-fd469e61bd4c"},
                        }
                    }
                },
                {
                    "PutRequest": {
                        "Item": {
                            "PK": {"S": "e04c537a-7177-4254-afae-594470849a2d"},
                            "SK": {"S": "85a05bd1-147a-4872-a830-cb6c7e229e08"},
                        }
                    }
                },
                {
                    "PutRequest": {
                        "Item": {
                            "PK": {"S": "e04c537a-7177-4254-afae-594470849a2d"},
                            "SK": {"S": "d3f475d5-301c-4482-9614-2b18d45b5a45"},
                        }
                    }
                }
        ]})
    ]

        self.assertEqual( test_return["statusCode"] , 200)
        self.assertEqual( test_return["body"] , "Kinesis events processed and persisted to DynamoDB table")