"""
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""

INPUT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "object",
    "title": "Sample Input schema",
    "description": "The root schema comprises the entire JSON document of the Input Schema.",
    "examples": [{"Unicorn Name": "Hello Unicorn", "Unicorn Location": "Some Location" }],
    "required": ["Unicorn Name", "Unicorn Location"],
    "properties": {
        "Unicorn Name": {
            "type": "string",
            "title": "The Unicorn's Name",
            "examples": ["Donner", "Dancer"]
        },
        "Unicorn Location": {
            "type": "string",
            "title": "The Unicorn's Location",
            "examples": ["US","CAN"]
        }
    }
}

OUTPUT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "object",
    "title": "Sample Output schema",
    "description": "The root schema comprises the entire JSON document of the Output Schema.",
    "examples": [{"Unicorn Name": "Hello Unicorn", "Unicorn Location": "Some Location" }],
    "required": ["PK", "LOCATION", "STATUS"],
    "properties": {
        "PK": {
            "type": "string",
            "title": "The Unicorn's Name",
            "examples": ["Donner", "Dancer"]
        },
        "LOCATION": {
            "type": "string",
            "title": "The Unicorn's Location",
            "examples": ["US","CAN"]
        },
        "STATUS": {
            "type": "string",
            "title": "The Unicorn's Status",
            "examples": ["AVAILABLE","IN-TRAINING"]
        }
    }
}