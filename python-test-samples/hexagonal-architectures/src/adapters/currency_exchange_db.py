"""
Currentcy Exchange DB Adapter
"""
from os import environ
import boto3

def get_currencies(currencies):
    """
    get_currencies: Gets the currencies from the DynamoDB table.
    """
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
    except Exception as err:
        print("get_currencies Error:" + str(err) + " : " + str(type(err)))
        raise err
    