# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
from urllib import response
import boto3
import pytest
from moto import mock_aws  # Changed from mock_s3
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from src import app


@pytest.fixture()
def apigw_event() ->  APIGatewayProxyEvent:
    with open(f"events/unit-test-event.json") as f:
        return APIGatewayProxyEvent(json.load(f))


@mock_aws  # Changed from @mock_s3
def test_lambda_handler(apigw_event: dict) -> None:

    # set up test bucket
    s3_client = boto3.client('s3', region_name='us-east-1')  # Added region for consistency
    test_bucket_names = ["test_bucket1","test_bucket2"]
    test_data = b'col_1,col_2\n1,2\n3,4\n'
    for test_bucket_name in test_bucket_names:
        s3_client.create_bucket(Bucket=test_bucket_name)    
        s3_client.put_object(Body=test_data, Bucket=test_bucket_name, Key=f'example/s3/path/key/test_data.csv')

    # call lambda function handler with synthetic event 
    test_response = app.lambda_handler(apigw_event, "")
    test_response_data =  test_response["body"].split("|")

    # evaluate response
    assert test_response["statusCode"] == 200
    assert test_bucket_names[0] in test_response_data
    assert test_bucket_names[1] in test_response_data
    assert len(test_response_data) == 2