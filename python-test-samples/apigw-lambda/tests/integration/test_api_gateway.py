# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import json
from unittest import TestCase

import boto3
import requests

"""
To run this integration test

\1 Set AWS_SAM_STACK_NAME environment variable to the stack to test
\2 Run the tests with the pytest module 
 
AWS_SAM_STACK_NAME=<stack-name> python -m pytest -s tests/integration -v
"""

class TestApiGateway(TestCase):
    api_endpoint: str

    @classmethod
    def get_stack_name(cls) -> str:
        stack_name = os.environ.get("AWS_SAM_STACK_NAME")
        if not stack_name:
            raise Exception(
                "Environment variable AWS_SAM_STACK_NAME does NOT exist.\n"
                "Resolve by setting AWS_SAM_STACK_NAME to the stack name for integration tests."
            )

        return stack_name

    def setUp(self) -> None:
        """
        With the provided ENV variable AWS_SAM_STACK_NAME, use the 
        CloudFormation API to lookup the HelloWorldApi URL.
        """
        stack_name = TestApiGateway.get_stack_name()

        client = boto3.client("cloudformation")

        try:
            response = client.describe_stacks(StackName=stack_name)
        except Exception as e:
            raise Exception(
                f'No stack found in the cloud with name: "{stack_name}"\n'
                f'Resolve by verifying the stack name is correct, and the stack is deployed.'
            ) from e

        stacks = response["Stacks"]

        stack_outputs = stacks[0]["Outputs"]
        print("\n\n--> Stack outputs:")
        for stack_output in stack_outputs:
            print()
            print(f'  {stack_output["OutputKey"]}')
            print(f'  = {stack_output["OutputValue"]}')
            print(f'  > {stack_output["Description"]}')

        api_outputs = [output for output in stack_outputs if output["OutputKey"] == "HelloWorldApi"]
        self.assertTrue(api_outputs, f"Cannot find output HelloWorldApi in stack {stack_name}")

        self.api_endpoint = api_outputs[0]["OutputValue"]
        print(f'\n--> Found API endpoint for "{stack_name}" stack...\n--> {self.api_endpoint}')

    def test_api_gateway(self):
        """
        Call the API Gateway endpoint and check the response
        """
        response = requests.get(self.api_endpoint)
        print("API Gateway response:")
        print(response.text)

        self.assertEqual(response.status_code, requests.codes.ok)
