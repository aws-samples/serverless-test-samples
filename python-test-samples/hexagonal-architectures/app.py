# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# Lambda Handler for the Python apigw-lambda-dynamodb example
# This handler accepts an id that represents a persons name, and creates a "Hello {Name}!" message.
# The id and name associated with the name is stored in a DynamoDB Table.
# Additionally, when a message is created, the lambda logs the "Hello {Name}!" message to DynamoDB with a timestamp.
# The DynamoDB Table used is passed as an environment variable "DYNAMODB_TABLE_NAME"

from os import environ
from datetime import datetime
from adapters import HandleStockRequest

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import validator

def lambda_handler(event: APIGatewayProxyEvent, context: LambdaContext) -> dict:
    try:
        print("test")
        print(event)
        stockID = event["pathParameters"]["stock"]
        print("Test")
        response = HandleStockRequest.getStocksRequest(stockID)
        return response
    except Exception as e:
        print(e)