# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# Placeholder Lambda Handler for the Python example
# The DynamoDB Table used is passed as an environment variable "DYNAMODB_TABLE_NAME"
from os import environ
import boto3
import json

from aws_xray_sdk.core import patch_all

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import validator

from schemas import OUTPUT_SCHEMA
patch_all()

# Logic to implement:
# Return a list of Unicorns
# Use the GSI_LOCATION if a location is specified as a query parameter
# Support page_token pagination as a query parameter


@validator(outbound_schema=OUTPUT_SCHEMA)
def lambda_handler(event: APIGatewayProxyEvent, context: LambdaContext) -> dict:

    # Retrieve the table name from the environment, and create a boto3 Table object
    dynamodb_table_name = environ["DYNAMODB_TABLE_NAME"]
    dynamodb_resource = boto3.resource('dynamodb')
    dynamodb_table = dynamodb_resource.Table(dynamodb_table_name)
    
    # Add Logic Here
    # All inline so it has to be fixed :-)

    status_code = 200
    body_payload = { "unicorn_list" : [ { "Name": "Unicorn A", "Location": "Florida", "Status": "AVAILABLE" } ],
                     "page_token" : "None" }
    
    return {
        "statusCode": status_code,
        "body": json.dumps(body_payload)
    }