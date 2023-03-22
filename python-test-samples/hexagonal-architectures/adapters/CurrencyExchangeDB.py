from os import environ
import json
import boto3

def getCurrencies(currencies):
    try:
        dynamodb_table_name = environ["CURRENCIES_DB_TABLE"]
        dynamodb_resource = boto3.resource('dynamodb')
        dynamodb_table = dynamodb_resource.Table(dynamodb_table_name)
        print(f"Using DynamoDB Table {dynamodb_table_name}.")
        rates = {}
        for currency in currencies:
            dynamodb_response = dynamodb_table.get_item(Key={"CURRENCY": f"{currency}"})
            print(dynamodb_response)
        #stockData = HttpHandler.retrieveStock(stockID)
        response = {
            "rates":{
                "USD": 1.21,
                "CAD": 1.31,
                "AUD": 1.41
            }
        }
        return response
    except Exception as e:
        print(e)