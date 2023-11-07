# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

OUTPUT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "$id": "http://example.com/example.json",
    "type": "object",
    "title": "Sample Output schema",
    "description": "The root schema comprises the entire JSON document of the Return Schema.",
    "examples": [{"statusCode": 200, "body": "Hello Tom Smith!"}],
    "required": ["statusCode", "body"],
    "properties": {
        "statusCode": {
            "$id": "#/properties/statusCode",
            "type": "integer",
            "title": "HTTP Status Code",
            "examples": [200,401,500]
        },
        "body": {
            "$id": "#/properties/body",
            "type": "string",
            "title": "The hello message",
            "examples": ["Hello Tom Smith!","Error","Error"],
            "maxLength": 20480,
        }
    },
}