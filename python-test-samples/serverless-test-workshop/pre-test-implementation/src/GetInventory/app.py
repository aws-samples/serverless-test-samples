# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# Placeholder Lambda Handler for the Python example
# The DynamoDB Table used is passed as an environment variable "DYNAMODB_TABLE_NAME"
from os import environ
import boto3
import json
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

    # Retrieve the table name from the environment, and create a boto3 Table object
    dynamodb_table_name = environ["DYNAMODB_TABLE_NAME"]
    dynamodb_index_name = environ["DYNAMODB_INDEX_NAME"]
    dynamodb_table = boto3.resource('dynamodb').Table(dynamodb_table_name)
    
    # Add Logic Here
    # All inline so it has to be fixed :-)

    location = event["pathParameters"]["location"]

    if event.get("queryStringParameters") is not None:
        page_token = event["queryStringParameters"].get("page_token")
    else:
        page_token = None

    if page_token is None:
        response = dynamodb_table.query(IndexName=dynamodb_index_name, 
                                        KeyConditionExpression=Key('LOCATION').eq(location))
    else:
        response = dynamodb_table.query(IndexName=dynamodb_index_name, 
                                KeyConditionExpression=Key('LOCATION').eq(location),
                                ExclusiveStartKey=json.loads(page_token))

    items_list = [ {"Name": item["PK"],"Location":item["LOCATION"],"Status":item["STATUS"]}
                   for item in response['Items']]
    
    last_key = response.get("LastEvaluatedKey","END")

    status_code = 200
    body_payload = { "unicorn_list" : items_list,
                     "page_token" : last_key }
    
    return {
        "statusCode": status_code,
        "body": json.dumps(body_payload)
    }