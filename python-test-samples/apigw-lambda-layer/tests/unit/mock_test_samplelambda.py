# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import sys
import pytest
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent

sys.path.append("src/sampleCodeLayer/python")
sys.path.append("src/sampleSchemaLayer/python")
from src.sampleLambda import app

@pytest.fixture()
def apigw_event() ->  APIGatewayProxyEvent:
    with open(f"events/unit-test-event.json") as f:
        return APIGatewayProxyEvent(json.load(f))

def test_lambda_handler(apigw_event: dict, mocker) -> None:

    mocker.patch("src.sampleLambda.app.get_s3_bucket_list_as_string", 
            return_value="bucket1|bucket2")

    # call lambda function handler with synthetic event 
    test_response = app.lambda_handler(apigw_event, "")
    test_response_data =  test_response["body"].split("|")

    assert test_response["statusCode"] == 200
    assert "bucket1" in test_response_data
    assert "bucket2" in test_response_data



