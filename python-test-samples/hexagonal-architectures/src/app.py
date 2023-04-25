# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# Lambda Handler for the Python hexagonal-architectures example
# This handler accepts a stock ID and provides the price of the stock in four currencies.
# The id and price in Euros associated with the stock is stored in a DynamoDB Table.
# The currency conversion rates for Euros to USD, CAD, and AUD are stored in another DynamoDB table. 

from os import environ
from datetime import datetime
from src.adapters import HandleStockRequest

# from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
# from aws_lambda_powertools.utilities.typing import LambdaContext
# from aws_lambda_powertools.utilities.validation import validator

def lambda_handler(event, context) -> dict:
    try:
        print(event)
        stockID = event["pathParameters"]["StockID"]
        response = HandleStockRequest.getStocksRequest(stockID)
        print("Response", response)
        return response
    except ValueError as e:
        print("V", e)
        return {
            "statusCode": 404,
            "body": "Stock not found"
        }
    except Exception as e:
        raise