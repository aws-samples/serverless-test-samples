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
    
    s3 = boto3.client('s3')
    # Iterates through all the objects, doing the pagination for you. Each obj
    # is an ObjectSummary, so it doesn't contain the body. You'll need to call
    # get to get the whole body.

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    print(f"processing {bucket}/{key}")
    status_code = 200
    data = s3.get_object(Bucket=bucket, Key=key)
    contents = data['Body'].read().decode()
    count = 0
    for entry in contents.split("\n"):
        print(f"Add {entry}")
        if "Unicorn" not in entry:
            (unicorn_name, unicorn_location) = entry.strip().split(",")

            response = dynamodb_table.put_item(
                Item={
                    'PK': unicorn_name,
                    'LOCATION': unicorn_location,
                    'STATUS' : "AVAILABLE"
                }
            )
            status_code = response['ResponseMetadata']['HTTPStatusCode']
            count += 1

    return {
        "statusCode": status_code,
        "body": f"{count} unicorns uploaded."
    }