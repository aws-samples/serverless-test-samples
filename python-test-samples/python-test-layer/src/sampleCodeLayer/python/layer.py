# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3

def get_s3_bucket_list_as_string() -> str:

    print("Hello layer!")
    
    s3_client = boto3.client('s3')
    s3_response = s3_client.list_buckets()

    bucket_list_string = "|".join([x["Name"] for x in s3_response["Buckets"]])
    
    return bucket_list_string