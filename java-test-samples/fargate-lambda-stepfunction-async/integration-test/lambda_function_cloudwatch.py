import os
import aiohttp
import asyncio
import json
import requests
import unittest
import boto3
from unittest.mock import patch
from MyCustomException import MyCustomException

def lambda_handler(event, context):
    try:
        # Call the helper function to make the API call
                # Process each SQS record in the event
        for record in event['Records']:
            # Get the message body from the SQS record
            message_body = json.loads(record['body'])
            #print(f'Message from SQS :', {message_body})
            print(f'SQS Record : {record}')

            # Call the helper function to make the API call
            request_id = asyncio.run(make_async_api_call(message_body))

            # Print the requestId obtained from the API
            print(f'Received message with request_id: {request_id}')

        # Print the requestId obtained from the API
        print(f'UUID: {request_id}')
        send_to_another_sqs_queue(request_id)

        # Return a JSON response
        return {
            'statusCode': 200,
            'body': json.dumps({'uuid': request_id}),
        }
    except MyCustomException as e:
        # Handle the custom exception and return an error response
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
        }

async def make_async_api_call(event):
        api_url = os.environ['API_URL']
        payload = event

async with aiohttp.ClientSession() as session:
    async with session.post(api_url, json=payload) as response:
        api_data = await response.json()

    return api_data.get('uuid', None)

def send_to_another_sqs_queue(message_body):
    # Specify the AWS region and the name of the target SQS queue
    region = os.environ['REGION']
    print('sending to SQS - 1',region)
    target_queue_url = os.environ['TARGET_QUEUE']

    # Create an SQS client
    sqs_client = boto3.client('sqs', region_name=region)

    # Send the message to the target SQS queue
    response = sqs_client.send_message(
        QueueUrl=target_queue_url,
        #MessageBody=json.dumps(message_body)
        MessageBody=json.dumps({'orderId': message_body})
    )

    print(f'Message sent to another SQS queue. Response: {response}')

# Run the event loop
if __name__ == "__main__":
    asyncio.run(main())