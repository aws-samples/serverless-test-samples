"""
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Lambda Function to retrieve the list of Locations
# The DynamoDB Table used is passed as an environment variable "DYNAMODB_TABLE_NAME"
# Logic:
# Retrieve and return the DynamoDB element "LOCATION#LIST"
"""

from os import environ
import json
import boto3

from aws_xray_sdk.core import patch_all

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import validator

from schemas import OUTPUT_SCHEMA
patch_all()

@validator(outbound_schema=OUTPUT_SCHEMA)
def lambda_handler(event: APIGatewayProxyEvent, context: LambdaContext) -> dict:
    """
    In this Lambda Function, all of the logic is in the handler.  
    It returns 400 if the unicorn is not found or is not available.
    Otherwise, it will reserve the unicorn for the name indicated.
    """

    # Retrieve the table name from the environment, and create a boto3 Table object
    dynamodb_table_name = environ["DYNAMODB_TABLE_NAME"]
    dynamodb_resource = boto3.resource("dynamodb")
    dynamodb_table = dynamodb_resource.Table(dynamodb_table_name)

   # Creating the DynamoDB Table Resource
    response = dynamodb_table.get_item( Key={"PK": "LOCATION#LIST"})
    if "Item" not in response:
        status_code = 400
        body_payload = {"locations":[]}
    else:
        status_code = 200
        body_payload = {"locations": response["Item"]["LOCATIONS"]}
        
    return {
        "statusCode": status_code,
        "body": json.dumps(body_payload)
    }