"""
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# The lambda is used as a trigger for the apigw-sqs-lambda example (POST request).
# This handler accepts messages from the input queue and deliver it to the output queue.
# The lambda uses OUTPUT_QUEUE_NAME environment variable to retrieve the name of the output queue.
"""

from os import environ
import logging
import json
import boto3

sqs_client = boto3.client('sqs')


def lambda_handler(event, context) -> dict:
    """
    The main lambda handler. will be called by the API Gateway.
    """
    # Retrieve the output Q name from the environment
    sqs_output_name = environ["OUTPUT_QUEUE_NAME"]
    logging.debug("Using sqs_output_name: %s", sqs_output_name)

    # Go over the events/records recieved from the input Q and send them to the output queue
    for record in event['Records']:
        payload = record["body"]
        try:
            message = sqs_client.send_message(
                QueueUrl=sqs_output_name, MessageBody=payload)
        except Exception as error:
            raise error
    return {
        'statusCode': 200,
        'body': json.dumps(message, indent=2)
    }
