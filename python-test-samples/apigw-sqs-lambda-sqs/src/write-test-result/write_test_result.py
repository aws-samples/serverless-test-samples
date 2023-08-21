"""
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# The lambda is used as a trigger for the apigw-sqs-lambda-sqs example.
# This lambda is triggered by the SQS OutputQueue or by the SQS InputQueueDLQ.
# Triggered by the SQS OutputQueue (indication the test is completed properly)- the lambda will receive the message from the output queue, process it and write the result of the test to the DynamoDB Table.
# Triggered by the SQS InputQueueDLQ (indication the test is failed due to an execption) - the lambda will receive the message from the DLQ queue, process it and write the result of the test to the DynamoDB Table.
# The lambda uses OUTPUT_QUEUE_NAME environment variable to retrieve the name of the output queue.
"""

from os import environ
import logging
import json
import boto3

sqs_client = boto3.client('sqs')


def lambda_handler(event, context) -> dict:
    """
    The main lambda handler. will be called by the SQS OutputQueue or by the SQS InputQueueDLQ.
    """
     # Retrieve the table name from the environment, and create a boto3 Table object
    dynamodb_table_name = environ["DYNAMODB_TABLE_NAME"]
    dynamodb_resource = boto3.resource('dynamodb')
    dynamodb_table = dynamodb_resource.Table(dynamodb_table_name)
    print(f"Using DynamoDB Table {dynamodb_table_name}.")

    # Go over the events/records recieved from Q and write the results to DynamoDB table
    for record in event['Records']:
        payload = record["body"]
        logging.debug(str(payload))