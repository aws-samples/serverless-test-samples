"""
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# Lambda Handler for the Python kinesis-lambda-dynamodb example
# This handler accepts a stream if kinesis events.
# The event data is persisted to Dynamo DB
# The DynamoDB Table used is passed as an environment variable "DYNAMODB_TABLE_NAME"
"""

from os import environ
import json
import base64
import boto3

from aws_lambda_powertools.utilities.data_classes import KinesisStreamEvent
from aws_lambda_powertools.utilities.typing import LambdaContext


# Retrieve the table name from the environment, and create a boto3 Table object
dynamodb_table_name = environ["DYNAMODB_TABLE_NAME"]
dynamodb_resource = boto3.Session(region_name="us-east-1").resource('dynamodb')
dynamodb_table = dynamodb_resource.Table(dynamodb_table_name)

def lambda_handler(event: KinesisStreamEvent, context: LambdaContext) -> dict:
    """
    # Function to read Kinesis stream and insert into DynamoDB table
    """
    print(f"Using DynamoDB Table {dynamodb_table_name}.")
    records = event["Records"]
    batch_size = 25  # maximum number of items to write at once
    # Create an empty list to store items to be written
    items_to_write = []
    # Iterate through records and add each one to the list
    for record in records:
        #data = json.loads(record['kinesis']['data'])
        data = base64.b64decode(record['kinesis']['data']).decode('ascii')
        payload_dict = json.loads(data)
        item = {'PK': payload_dict['batch'], 'SK': payload_dict['id']}
        items_to_write.append(item)
        # If the list is at the batch size, write the items to the table and clear the list
        if len(items_to_write) >= batch_size:
            write_to_dynamodb(items_to_write)
            items_to_write = []
    # If there are any remaining items in the list, write them to the table
    if items_to_write:
        write_to_dynamodb(items_to_write)
    return {
        "statusCode": 200,
        "body": "Kinesis events processed and persisted to DynamoDB table"
    }

def write_to_dynamodb(items):
    """
    # Function to Write to DynamoDB table
    """
    with dynamodb_table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)
            