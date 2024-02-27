"""
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Lambda Function to reserve a Unicorn
# The DynamoDB Table used is passed as an environment variable "DYNAMODB_TABLE_NAME"
# Logic:
# Given unicorn (Unicorn Name) and (reserved_for) in the body payload
# Verify the Unicorn is available, if not return error status
# Update status to RESERVED
"""

from os import environ
import urllib
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

    post_payload = {}
    for item in event["body"].split("&"):
        post_payload[item.split("=")[0]] = urllib.parse.unquote_plus(item.split("=")[1])

    unicorn_to_checkout = post_payload["unicorn"]
    checkout_to_name = post_payload["reserved_for"]

   # Creating the DynamoDB Table Resource
    response = dynamodb_table.get_item( Key={"PK": unicorn_to_checkout})
    if "Item" not in response or response["Item"]["STATUS"] != "AVAILABLE":
        status_code = 400
        body_payload = f"{unicorn_to_checkout} Not Available"
    else:
        response = dynamodb_table.update_item(
                Key={"PK": unicorn_to_checkout},
                UpdateExpression="SET #s = :val1, #r = :val2",
                ExpressionAttributeValues={
                    ":val1": "RESERVED",
                    ":val2": checkout_to_name
                },
                ExpressionAttributeNames={
                    "#s":"STATUS",
                    "#r":"RES_BY"
                }
            )
        status_code = 200
        body_payload = "OK"
        
    return {
        "statusCode": status_code,
        "body": body_payload
    }