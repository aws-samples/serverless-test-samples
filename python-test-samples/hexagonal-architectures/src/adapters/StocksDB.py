from os import environ
import json
import boto3
from botocore.exceptions import ClientError


def getStockValue(stockID):
    try:
        dynamodb_table_name = environ["STOCKS_DB_TABLE"]
        dynamodb_resource = boto3.resource('dynamodb')
        dynamodb_table = dynamodb_resource.Table(dynamodb_table_name)
        print(f"Using DynamoDB Table {dynamodb_table_name}.")
        dynamodb_response = dynamodb_table.get_item(Key={"STOCK_ID": f"{stockID}"})
        if "Item" not in dynamodb_response:
            raise ValueError("Stock not found")
        print("dynamodb response", dynamodb_response)
        return dynamodb_response
    except Exception as e:
        print(e)
        raise