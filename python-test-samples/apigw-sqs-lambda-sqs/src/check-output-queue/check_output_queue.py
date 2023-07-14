"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

The lambda is used as a trigger for the apigw-sqs-lambda example (Get request API).
This handler retrive messages from the output queue and return as response to API Gatway
The OUTPUT_QUEUE_NAME environment variable is used to specify the name of the output queue.
"""

from os import environ
import logging
import json
import boto3


sqs_client = boto3.client('sqs')

"""
lambda_handler is the entry point of the lambda function.
It retrieves one message from the output queue 
and return it to API Gatway as a response. 
"""


def lambda_handler(event, context) -> dict:
    """
    main function to retrieve one message from the output queue
    and return it to API Gatway as a response.

    Args:
        event (dict): event passed by API Gatway
        context (dict): context passed by API Gatway

    Returns:
        dict: response to API Gatway
    """
    # Retrieve the output Q name from the environment
    sqs_output_name = environ["OUTPUT_QUEUE_NAME"]
    response = {}
    logging.debug("Using sqs_output_name: %s", sqs_output_name)
    try:
        # By default only one message will be read at a time
        message = sqs_client.receive_message(
            QueueUrl=sqs_output_name, MessageAttributeNames=['All'])
        # check if the message is empty
        if "Messages" not in message:
            response = {
                'statusCode': 404,
                'body': json.dumps('No message in the output queue')
            }
        else:
            # Delete message from queue
            sqs_client.delete_message(QueueUrl=sqs_output_name,
                                      ReceiptHandle=message['Messages'][0]['ReceiptHandle'])
            response = {
                'statusCode': 200,
                'body': json.dumps(message, indent=2)
            }
    except Exception as error:
        raise error

    return response
