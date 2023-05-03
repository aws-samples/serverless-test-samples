"""
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

Lambda Handler for the Python hexagonal-architectures example
This handler accepts a stock ID and provides the price of the stock in four currencies.
The id and price in Euros associated with the stock is stored in a DynamoDB Table.
The currency conversion rates for Euros to USD, CAD, and AUD are stored in another DynamoDB table.
"""
from src.adapters import handle_stock_request

# from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
# from aws_lambda_powertools.utilities.typing import LambdaContext
# from aws_lambda_powertools.utilities.validation import validator

def lambda_handler(event, context) -> dict:
    """
    lambda_handler: Entry Point
    """
    try:
        stock_id = event["pathParameters"]["StockID"]
        response = handle_stock_request.get_stocks_request(stock_id)
        return response
    except ValueError as err:
        print("lambda_handler ValueError:" + str(err) + " : " + str(type(err)))
        return {
            "statusCode": 404,
            "body": "Stock not found"
        }
    except Exception as err:
        print("lambda_handler Error:" + str(err) + " : " + str(type(err)))
        raise err
