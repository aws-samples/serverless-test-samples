"""
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# Lambda Function to retrieve a Unicorn Inventory
#   Requires pathParameters.location to specify LOCATION
#   Optionally, if queryStringParameters.available is True, it will filter to only available
#      unicorns.
#   
# The DynamoDB Table used is passed as an environment variable "DYNAMODB_TABLE_NAME"
# The DynamoDB Index used is passed as an environment variable "DYNAMODB_INDEX_NAME"
"""

from os import environ
import json
import boto3
from boto3.dynamodb.conditions import Key
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
    """
    Lambda Handler for an API Gateway Event
    """

    # Retrieve the table name from the environment, and create a boto3 Table object
    dynamodb_table_name = environ["DYNAMODB_TABLE_NAME"]
    dynamodb_index_name = environ["DYNAMODB_INDEX_NAME"]
    dynamodb_table = boto3.resource('dynamodb').Table(dynamodb_table_name)

    # Location is required
    location = event["pathParameters"]["location"]

    # Optional filter to available
    if event.get("queryStringParameters") is not None and \
        ( event["queryStringParameters"].get("available", "False").lower() == "true" ):
        key_expression = Key("LOCATION").eq(location) & Key("STATUS").eq("AVAILABLE")
    else:
        key_expression = Key("LOCATION").eq(location)

    # Optional pagination token
    if event.get("queryStringParameters") is not None:
        page_token = event["queryStringParameters"].get("page_token")
    else:
        page_token = None

    # Query
    if page_token is None:
        response = dynamodb_table.query(IndexName=dynamodb_index_name,
                                        KeyConditionExpression=key_expression)
    else:
        response = dynamodb_table.query(IndexName=dynamodb_index_name,
                                KeyConditionExpression=key_expression,
                                ExclusiveStartKey=json.loads(page_token))

    items_list = [ {"Name": item["PK"],"Location":item["LOCATION"],
                    "Status":item["STATUS"], 
                    "Reserved By":item.get("RES_BY","- available -")}
                   for item in response["Items"]]

    last_key = response.get("LastEvaluatedKey","END")

    status_code = 200
    body_payload = { "unicorn_list" : items_list,
                     "page_token" : last_key }

    return {
        "statusCode": status_code,
        "body": json.dumps(body_payload)
    }
