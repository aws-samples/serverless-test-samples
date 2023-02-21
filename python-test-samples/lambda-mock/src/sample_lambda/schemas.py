"""
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# Start of lambda schema definition code:  src/sampleLambda/schema.py
"""

INPUT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "$id": "http://example.com/example.json",
    "type": "object",
    "title": "Sample input schema",
    "description": "The Document generation path parameters, Document Type and Customer ID.",
    "required": ["pathParameters"],
    "properties": {
        "pathParameters" : { 
            "$id": "#/properties/pathParameters",
            "type": "object",
            "required": ["docType", "customerId"],
            "properties": {
                "docType": {
                    "$id": "#/properties/pathParameters/docType",
                    "type": "string",
                    "title": "The Document Type to Generate",
                    "examples": ["TestDoc","WELCOME"],
                    "maxLength": 30,
                    },
                "customerId": {
                    "$id": "#/properties/pathParameters/customerId",
                    "type": "string",
                    "title": "The Customer ID to send the document",
                    "examples": ["TestCustomer","TestCustomer01"],
                    "maxLength": 30,
                }
            }
        }
    },
}

OUTPUT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "$id": "http://example.com/example.json",
    "type": "object",
    "title": "Sample outgoing schema",
    "description": "The root schema comprises the entire JSON document.",
    "examples": [{"statusCode": 200, "body": "OK"}],
    "required": ["statusCode", "body"],
    "properties": {
        "statusCode": {"$id": "#/properties/statusCode", "type": "integer", "title": "The statusCode"},
        "body": {"$id": "#/properties/body", "type": "string", "title": "The response"}
    },
}

# End of schema definition code
