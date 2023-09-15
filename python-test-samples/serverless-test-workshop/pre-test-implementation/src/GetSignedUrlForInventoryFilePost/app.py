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
import logging
import uuid
from datetime import datetime
from botocore.exceptions import ClientError
from aws_xray_sdk.core import patch_all

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import validator

from schemas import OUTPUT_SCHEMA
patch_all()


def create_presigned_post(bucket_name, object_name,
                          fields=None, conditions=None, expiration=3600):
    """Generate a presigned URL S3 POST request to upload a file
    Source: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html
    :param bucket_name: string
    :param object_name: string
    :param fields: Dictionary of prefilled form fields
    :param conditions: List of conditions to include in the policy
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Dictionary with the following keys:
        url: URL to post to
        fields: Dictionary of form fields and values to submit with the POST
    :return: None if error.
    """

    # Generate a presigned S3 POST URL
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_post(bucket_name,
                                                     object_name,
                                                     Fields=fields,
                                                     Conditions=conditions,
                                                     ExpiresIn=expiration)
    except ClientError as err_client:
        logging.error(err_client)
        raise(err_client)

    # The response contains the presigned URL and required fields
    return response


@validator(outbound_schema=OUTPUT_SCHEMA)
def lambda_handler(event: APIGatewayProxyEvent, context: LambdaContext) -> dict:

    # Retrieve the bucket name from the environment, and create a boto3 s3 resource
    s3_bucket_name = environ["S3_BUCKET_NAME"]
    
    # Business Logic that should be tested: Compute an upload file name
    # Create a prefix for year/month/day, and name the file unicorn_load_DATETIME_UUID.csv
    datetime_stamp = datetime.now().strftime('%Y%m%dT%H%M%S')
    file_prefix = datetime.now().strftime('%Y/%m/%d')
    unique_id = str(uuid.uuid4())
    file_key = f"{file_prefix}/unicorn_load_{datetime_stamp}_{unique_id}.csv"

     
    # Retrieve Pre-Signed URL for a POST operation
    pre_signed_url = create_presigned_post(s3_bucket_name, file_key)

    status_code = 200
        
    return {
        "statusCode": status_code,
        "body": json.dumps(pre_signed_url)
    }