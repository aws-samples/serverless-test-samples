# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
from aws_xray_sdk.core import patch_all

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import validator

try:
    from schemas import OUTPUT_SCHEMA
    patch_all()
except:
    from src.schemas import OUTPUT_SCHEMA


@validator(outbound_schema=OUTPUT_SCHEMA)
def lambda_handler(event: APIGatewayProxyEvent, context: LambdaContext) -> dict:

    s3_client = boto3.client('s3')
    s3_response = s3_client.list_buckets()

    bucket_list = "|".join([x["Name"] for x in s3_response["Buckets"]])
    
    print("Hello logfile!")

    return {
        "statusCode": 200,
        "body": bucket_list
    }



