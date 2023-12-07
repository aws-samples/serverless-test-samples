"""
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

Compile a unique list of sorted Unicorn Locations.
"""
import os
import boto3


def lambda_handler(event, _):
    """
    Given a list of Unicorns Processed, put the unique locations in a quick lookup record
    """

    dynamodb = boto3.resource('dynamodb')
    dynamodb_table_name = os.environ["DYNAMODB_TABLE_NAME"]
    table = dynamodb.Table(dynamodb_table_name)

    locations = [x["LOCATION"] for x in event]

    # Append the Current List
    response = table.get_item(
    Key={
        'PK': "LOCATION#LIST"
        }
    )

    location_set = set()
    for l in locations:
        location_set.add(l)
    if "Item" in response:
        for l in response["Item"]["LOCATIONS"]:
            location_set.add(l)
    location_list_sorted = [x for x in sorted(location_set)]

    response = table.put_item(
        Item={
            'PK': "LOCATION#LIST",
            'LOCATIONS': location_list_sorted
        }
    )
    status_code = response['ResponseMetadata']['HTTPStatusCode']

    return {
        'statusCode': status_code,
        'body': "Put {} locations".format(len(location_list_sorted))
    }
