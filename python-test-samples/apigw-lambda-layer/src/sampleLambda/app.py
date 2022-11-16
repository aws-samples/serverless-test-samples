# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
from aws_xray_sdk.core import patch_all

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import validator
from schemas import OUTPUT_SCHEMA
from layer import get_s3_bucket_list_as_string
patch_all()
 

@validator(outbound_schema=OUTPUT_SCHEMA)
def lambda_handler(event: APIGatewayProxyEvent, context: LambdaContext) -> dict:

    print("Hello logfile!")
    bucket_list = get_s3_bucket_list_as_string()
    
    return {
        "statusCode": 200,
        "body": bucket_list
    }



