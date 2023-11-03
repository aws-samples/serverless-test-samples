"""
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

Validate a Unicorn name, assign an initial status, and convert data format
"""
import random
from aws_xray_sdk.core import patch_all
from aws_lambda_powertools.utilities.validation import validator
from schemas import INPUT_SCHEMA, OUTPUT_SCHEMA
patch_all()

@validator(inbound_schema=INPUT_SCHEMA, outbound_schema=OUTPUT_SCHEMA)
def lambda_handler(event, _):
    """
    Reformat the record and add a random initial status.
    Validate the Unicorn Name and location
    """

    if event.get("Unicorn Name", None) is None:
        raise Exception("Unicorn Name not provided")

    if event.get("Unicorn Location", None) is None:
        raise Exception("Unicorn Location not provided")

    if random.uniform(0, 1) < 0.20:
        initial_status = "IN_TRAINING"
    else:
        initial_status = "AVAILABLE"

    return {"PK":event["Unicorn Name"],
            "LOCATION":event["Unicorn Location"],
            "STATUS" : initial_status}
