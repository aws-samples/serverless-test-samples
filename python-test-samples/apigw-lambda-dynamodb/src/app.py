# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# Lambda Handler for the Python apigw-lambda-dynamodb example
# This handler accepts an id that represents a persons name, and creates a "Hello {Name}!" message.
# The id and name associated with the name is stored in a DynamoDB Table.
# Additionally, when a message is created, the lambda logs the "Hello {Name}!" message to DynamoDB with a timestamp.
# The DynamoDB Table used is passed as an environment variable "DYNAMODB_TABLE_NAME"

from os import environ
from datetime import datetime
import boto3

from aws_xray_sdk.core import patch_all

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import validator

try:
    from schemas import OUTPUT_SCHEMA
    patch_all()
except:
    from src.schemas import OUTPUT_SCHEMA


@validator(outbound_schema=OUTPUT_SCHEMA)
def lambda_handler(event: APIGatewayProxyEvent, context: LambdaContext) -> dict:

    # Retrieve the table name from the environment, and create a boto3 Table object
    dynamodb_table_name = environ["DYNAMODB_TABLE_NAME"]
    dynamodb_resource = boto3.resource('dynamodb')
    dynamodb_table = dynamodb_resource.Table(dynamodb_table_name)
    print(f"Using DynamoDB Table {dynamodb_table_name}.")

    # User id field is passed as a path parameter
    id = event["pathParameters"]["id"]

    # Retrieve the person's name from an id, and construct the message.
    dynamodb_response = dynamodb_table.get_item(Key={"PK": f"{id}", "SK": "NAME#"})
    print(dynamodb_response)

    # Does the person exist for this id?
    if "Item" in dynamodb_response and "data" in dynamodb_response["Item"]:
        person_name = dynamodb_response["Item"]["data"]
        hello_message = f"Hello {person_name}!"
        status_code = 200
    else:
        hello_message = f"ERROR: Name Not Found for ID {id}"
        status_code = 500

    # Create a timestamp and log the message back to DynamoDB
    datetime_stamp = "DT#" + datetime.now().strftime("%Y%m%dT%H%M%S.%f")
    dynamodb_table.put_item(Item={'PK'  : id,
                                  'SK'  : datetime_stamp, 
                                  'data': hello_message})

    # Log and return
    print(f"Message: {hello_message} - {datetime_stamp}")
        
    return {
        "statusCode": status_code,
        "body": hello_message
    }