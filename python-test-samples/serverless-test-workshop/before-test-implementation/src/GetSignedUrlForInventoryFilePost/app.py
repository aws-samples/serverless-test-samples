# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# Placeholder Lambda Handler for the Python apigw-lambda-dynamodb example
# The S3 Bucket used is passed as an environment variable "S3_BUCKET_NAME"

# Logic to implement:
#   Create a path/key with a datetime stamp in it
#   Generate and return a signed URL for the bucket/key

from os import environ
import boto3
import json
from aws_xray_sdk.core import patch_all

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import validator

from schemas import OUTPUT_SCHEMA
patch_all()



@validator(outbound_schema=OUTPUT_SCHEMA)
def lambda_handler(event: APIGatewayProxyEvent, context: LambdaContext) -> dict:

    # Retrieve the bucket name from the environment, and create a boto3 s3 resource
    s3_bucket_name = environ["S3_BUCKET_NAME"]
    s3_resource = boto3.resource('s3')
     
    # Add Logic Here
    # All inline so it has to be fixed :-)

    status_code = 200
    body_payload = "https://www.amazon.com"
        
    return {
        "statusCode": status_code,
        "body": json.dumps(body_payload)
    }