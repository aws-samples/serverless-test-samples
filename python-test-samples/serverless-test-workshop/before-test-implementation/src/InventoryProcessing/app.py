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


from os import environ
import boto3
from aws_xray_sdk.core import patch_all

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import validator

from schemas import OUTPUT_SCHEMA
patch_all()



@validator(outbound_schema=OUTPUT_SCHEMA)
def lambda_handler(event: APIGatewayProxyEvent, context: LambdaContext) -> dict:

    # Retrieve the table name from the environment, and create a boto3 Table object
    dynamodb_table_name = environ["DYNAMODB_TABLE_NAME"]
    dynamodb_resource = boto3.resource('dynamodb')
    dynamodb_table = dynamodb_resource.Table(dynamodb_table_name)
    
    # Add Logic Here
    # All inline so it has to be fixed :-)

    status_code = 200
    body_payload = "OK"
        
    return {
        "statusCode": status_code,
        "body": body_payload
    }