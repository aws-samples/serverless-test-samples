"""
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# Start of unit test code: tests/unit/src/test_sample_lambda.py
"""

import sys
import os
import json
from unittest import TestCase
from unittest.mock import MagicMock, patch
from boto3 import resource, client
from moto import mock_aws  # Changed from import moto
from aws_lambda_powertools.utilities.validation import validate

# [0] Import the Globals, Classes, Schemas, and Functions from the Lambda Handler
sys.path.append('./src/sample_lambda')
from src.sample_lambda.app import LambdaDynamoDBClass, LambdaS3Class   # pylint: disable=wrong-import-position
from src.sample_lambda.app import lambda_handler, create_letter_in_s3  # pylint: disable=wrong-import-position
from src.sample_lambda.schemas import INPUT_SCHEMA                     # pylint: disable=wrong-import-position

# [1] Mock all AWS Services in use
@mock_aws  # Changed from @moto.mock_dynamodb @moto.mock_s3
class TestSampleLambda(TestCase):
    """
    Test class for the application sample AWS Lambda Function
    """

    # Test Setup
    def setUp(self) -> None:
        """
        Create mocked resources for use during tests
        """

        # [2] Mock environment & override resources
        self.test_ddb_table_name = "unit_test_ddb"
        self.test_s3_bucket_name = "unit_test_s3_bucket"
        os.environ["DYNAMODB_TABLE_NAME"] = self.test_ddb_table_name
        os.environ["S3_BUCKET_NAME"] = self.test_s3_bucket_name

        # [3a] Set up the services: construct a (mocked!) DynamoDB table
        dynamodb = resource("dynamodb", region_name="us-east-1")
        dynamodb.create_table(
            TableName = self.test_ddb_table_name,
            KeySchema=[{"AttributeName": "PK", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "PK", "AttributeType": "S"}],
            BillingMode='PAY_PER_REQUEST'
            )

        # [3b] Set up the services: construct a (mocked!) S3 Bucket table
        s3_client = client('s3', region_name="us-east-1")
        s3_client.create_bucket(Bucket = self.test_s3_bucket_name )

        # [4] Establish the "GLOBAL" environment for use in tests.
        mocked_dynamodb_resource = resource("dynamodb")
        mocked_s3_resource = resource("s3")
        mocked_dynamodb_resource = { "resource" : resource('dynamodb'),
                                     "table_name" : self.test_ddb_table_name  }
        mocked_s3_resource = { "resource" : resource('s3'),
                               "bucket_name" : self.test_s3_bucket_name }
        self.mocked_dynamodb_class = LambdaDynamoDBClass(mocked_dynamodb_resource)
        self.mocked_s3_class = LambdaS3Class(mocked_s3_resource)


    def test_create_letter_in_s3(self) -> None:
        """
        Verify given correct parameters, the document will be written to S3 with proper contents.
        """

        # [5] Post test items to a mocked database
        self.mocked_dynamodb_class.table.put_item(Item={"PK":"D#UnitTestDoc",
                                                        "data":"Unit Test Doc Corpi"})
        self.mocked_dynamodb_class.table.put_item(Item={"PK":"C#UnitTestCust",
                                                        "data":"Unit Test Customer"})

        # [6] Run DynamoDB to S3 file function
        test_return_value = create_letter_in_s3(
                        dynamo_db = self.mocked_dynamodb_class,
                        s3=self.mocked_s3_class,
                        doc_type = "UnitTestDoc",
                        cust_id = "UnitTestCust"
                        )

        # [7] Ensure the data was written to S3 correctly, with correct contents
        bucket_key = "UnitTestCust/UnitTestDoc.txt"
        body = self.mocked_s3_class.bucket.Object(bucket_key).get()['Body'].read()

        # Test
        self.assertEqual(test_return_value["statusCode"], 200)
        self.assertIn("UnitTestCust/UnitTestDoc.txt", test_return_value["body"])
        self.assertEqual(body.decode('ascii'),"Dear Unit Test Customer;\nUnit Test Doc Corpi")


    def test_create_letter_in_s3_doc_type_notfound_404(self) -> None:
        """
        Verify given a document type not present in the data table, a 404 error is returned.
        """
        # [8] Post test items to a mocked database
        self.mocked_dynamodb_class.table.put_item(Item={"PK":"D#UnitTestDoc",
                                                        "data":"Unit Test Doc Corpi"})
        self.mocked_dynamodb_class.table.put_item(Item={"PK":"C#UnitTestCust",
                                                        "data":"Unit Test Customer"})

        # [9] Run DynamoDB to S3 file function
        test_return_value = create_letter_in_s3(
                            dynamo_db = self.mocked_dynamodb_class,
                            s3=self.mocked_s3_class,
                            doc_type = "NOTVALID",
                            cust_id = "UnitTestCust"
                            )

        # Test
        self.assertEqual(test_return_value["statusCode"], 404)
        self.assertIn("Not Found", test_return_value["body"])

    def test_create_letter_in_s3_customer_notfound_404(self) -> None:
        """
        Verify given a user id not present in the data table, a 404 error is returned.
        """

        # [10] Post test items to a mocked database
        self.mocked_dynamodb_class.table.put_item(Item={"PK":"D#UnitTestDoc",
                                                        "data":"Unit Test Doc Corpi"})
        self.mocked_dynamodb_class.table.put_item(Item={"PK":"C#UnitTestCust",
                                                        "data":"Unit Test Customer"})

        # [11] Run DynamoDB to S3 file function
        test_return_value = create_letter_in_s3(
                            dynamo_db = self.mocked_dynamodb_class,
                            s3=self.mocked_s3_class,
                            doc_type = "UnitTestDoc",
                            cust_id = "NOTVALID"
                            )

        # Test
        self.assertEqual(test_return_value["statusCode"], 404)
        self.assertIn("Not Found", test_return_value["body"])

    # [12] Load and validate test events from the file system
    def load_sample_event_from_file(self, test_event_file_name: str) ->  dict:
        """
        Loads and validate test events from the file system
        """
        event_file_name = f"tests/events/{test_event_file_name}.json"
        with open(event_file_name, "r", encoding='UTF-8') as file_handle:
            event = json.load(file_handle)
            validate(event=event, schema=INPUT_SCHEMA)
            return event

    # [13] Patch the Global Class and any function calls
    @patch("src.sample_lambda.app.LambdaDynamoDBClass")
    @patch("src.sample_lambda.app.LambdaS3Class")
    @patch("src.sample_lambda.app.create_letter_in_s3")
    def test_lambda_handler_valid_event_returns_200(self,
                            patch_create_letter_in_s3 : MagicMock,
                            patch_lambda_s3_class : MagicMock,
                            patch_lambda_dynamodb_class : MagicMock
                            ):
        """
        Verify the event is parsed, AWS resources are passed, the 
        create_letter_in_s3 function is called, and a 200 is returned.
        """

        # [14] Test setup - Return a mock for the global variables and resources
        patch_lambda_dynamodb_class.return_value = self.mocked_dynamodb_class
        patch_lambda_s3_class.return_value = self.mocked_s3_class

        return_value_200 = {"statusCode" : 200, "body":"OK"}
        patch_create_letter_in_s3.return_value = return_value_200

        # [15] Run Test using a test event from /tests/events/*.json
        test_event = self.load_sample_event_from_file("sampleEvent1")
        test_return_value = lambda_handler(event=test_event, context=None)

        # [16] Validate the function was called with the mocked globals
        # and event values
        patch_create_letter_in_s3.assert_called_once_with(
                                        dynamo_db=self.mocked_dynamodb_class,
                                        s3=self.mocked_s3_class,
                                        doc_type=test_event["pathParameters"]["docType"],
                                        cust_id=test_event["pathParameters"]["customerId"])

        self.assertEqual(test_return_value, return_value_200)


    def tearDown(self) -> None:

        # [13] Remove (mocked!) S3 Objects and Bucket
        s3_resource = resource("s3",region_name="us-east-1")
        s3_bucket = s3_resource.Bucket( self.test_s3_bucket_name )
        for key in s3_bucket.objects.all():
            key.delete()
        s3_bucket.delete()

        # [14] Remove (mocked!) DynamoDB Table
        dynamodb_resource = client("dynamodb", region_name="us-east-1")
        dynamodb_resource.delete_table(TableName = self.test_ddb_table_name )

# End of unit test code