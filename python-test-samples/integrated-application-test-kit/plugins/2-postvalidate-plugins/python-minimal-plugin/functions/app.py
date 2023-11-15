#Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#SPDX-License-Identifier: MIT-0

import json
import boto3

def lambda_handler(event, context):

    # Do some stuff here and validate that you've been successful
    valid = {
        "valid": True,
        "reason": "The plugin works!"
    }

    # Extract duration and taskToken from the incoming event
    taskToken = event["detail"]["taskToken"]

    eventToSend = { 
        "Source": "video.plugin.PythonMinimalPlugin",
        "DetailType": 'plugin-complete',
        "EventBusName": "default",
        "Detail": json.dumps({"TaskToken": taskToken,"Message":valid})
    }

    try:
        eventBridgeClient = boto3.client('events')
        eventBridgeClient.put_events(Entries=[eventToSend])
        return {
            "statusCode": 200,
            "body": "Success!"
        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "body": "Error!"
        }
