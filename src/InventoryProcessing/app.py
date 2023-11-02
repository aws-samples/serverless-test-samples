"""
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# Placeholder Lambda Handler for the Python apigw-lambda-dynamodb example
# The S3 Bucket used is passed as an environment variable "S3_BUCKET_NAME"

# Logic to implement:
#   Given a Bucket/Key passed in the S3 PutObject event
#   Make sure it is a CSV file with {Unicorn Name, Unicorn Location}
#   Add any Unicorns not in the database
#   Relocate Unicorns with changed locations
#   Retire any Unicorns in the database not in the file
#   If a Unicorn is RESERVED|RETIRED, do not modify it's entry - log/return an error
#   Update the available Unicorn count statistic in DynamoDB.  (PK = AVAILABLE, Value = #)
"""
import boto3
import os
import json
from aws_xray_sdk.core import patch_all
from aws_lambda_powertools.utilities.data_classes import S3Event
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import validator

from schemas import OUTPUT_SCHEMA
patch_all()
ikk
sf=boto3.client('stepfunctions')

@validator(outbound_schema=OUTPUT_SCHEMA)
def lambda_handler(event: S3Event, context: LambdaContext) :
    records = event['Records']
    print(records)
    s3_records = filter(lambda record: record['eventSource'] == 'aws:s3', records)
    object_created_records = filter(lambda record: record['eventName'].startswith('ObjectCreated'), s3_records)
    for record in object_created_records:
        key = record['s3']['object']['key']
        bucket=record['s3']['bucket']['name']
    sfInput={}
    sfInput['bucket']=bucket
    sfInput['key']=key
    print(sfInput)
    
    response = sf.start_execution(
        stateMachineArn = os.environ["SF_ARN"],
        input = json.dumps(sfInput))
    
    return {
        "statusCode": 200,
        "body": json.dumps(response)
    }