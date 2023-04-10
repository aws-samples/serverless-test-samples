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
            rates[dynamodb_response["Item"]["CURRENCY"]] = dynamodb_response["Item"]["Rate"]
        print(rates)
        return rates
    except Exception as e:
        print(e)