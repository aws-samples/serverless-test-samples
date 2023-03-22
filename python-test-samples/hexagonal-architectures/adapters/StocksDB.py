from os import environ
import json
import boto3

def getStockValue(stockID):
    try:
        dynamodb_table_name = environ["STOCKS_DB_TABLE"]
        dynamodb_resource = boto3.resource('dynamodb')
        dynamodb_table = dynamodb_resource.Table(dynamodb_table_name)
        print(f"Using DynamoDB Table {dynamodb_table_name}.")
        dynamodb_response = dynamodb_table.get_item(Key={"STOCK_ID": f"{stockID}"})
        dynamodb_response = {"STOCK_ID": "1", "VALUE": 3}
        return dynamodb_response
    except Exception as e:
        print(e)