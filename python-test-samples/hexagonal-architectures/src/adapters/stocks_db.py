"""
Stock Value DB Adapter
"""
from os import environ
import boto3

def get_stock_value(stock_id):
    """
    get_stock_value - retrieve a stock from the DB
    """
    try:
        dynamodb_table_name = environ["STOCKS_DB_TABLE"]
        dynamodb_resource = boto3.resource('dynamodb')
        dynamodb_table = dynamodb_resource.Table(dynamodb_table_name)
        print(f"Using DynamoDB Table {dynamodb_table_name}.")
        dynamodb_response = dynamodb_table.get_item(Key={"STOCK_ID": f"{stock_id}"})
        if "Item" not in dynamodb_response:
            raise ValueError("Stock not found")
        print("dynamodb response", dynamodb_response)
        return dynamodb_response
    except Exception as err:
        print("get_stock_value Error:" + str(err) + " : " + str(type(err)))
        raise err
    