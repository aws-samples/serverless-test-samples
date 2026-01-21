# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
from moto import mock_aws
from src.sampleCodeLayer.python.layer import get_s3_bucket_list_as_string

@mock_aws
def test_get_s3_bucket_list_as_string() -> None:

    # set up test bucket
    s3_client = boto3.client('s3', region_name='us-east-1')
    test_bucket_names = ["test_bucket1","test_bucket2"]
    test_data = b'col_1,col_2\n1,2\n3,4\n'
    for test_bucket_name in test_bucket_names:
        s3_client.create_bucket(Bucket=test_bucket_name)    
        s3_client.put_object(Body=test_data, Bucket=test_bucket_name, Key=f'example/s3/path/key/test_data.csv')

    # call lambda function handler with synthetic event 
    response_data = get_s3_bucket_list_as_string()
    test_response_data = response_data.split("|")

    # evaluate response
    assert test_bucket_names[0] in test_response_data
    assert test_bucket_names[1] in test_response_data
    assert len(test_response_data) == 2
