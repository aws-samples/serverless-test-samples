"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

Set the environment variable AWS_SAM_STACK_NAME to the name of the stack you deploied
> export AWS_SAM_STACK_NAME=<stack-name> 
> python -m pytest -s tests/integration -v 
"""

import os
import time
import logging
from unittest import TestCase
from uuid import uuid4
import boto3
import requests

class TestApiGateway(TestCase):
    """THe main test class for the API Gateway"""
    api_endpoint: str
    api_endpoint_inbox: str
    api_endpoint_outbox: str

    aws_region = os.environ.get("AWS_DEFAULT_REGION") or "us-east-1"

    @classmethod
    def get_stack_name(cls) -> str:
        """get stack name from environment variable AWS_SAM_STACK_NAME"""

        stack_name = os.environ.get("AWS_SAM_STACK_NAME")
        if not stack_name:
            raise EnvironmentError(
                "Cannot find env var AWS_SAM_STACK_NAME. \n"
                "Please setup this environment variable with the stack name\n")
        return stack_name

    @classmethod
    def setUp(self) -> None:
        """
        Based on the provided env variable AWS_SAM_STACK_NAME,
        We use the cloudformation API to retrieve the APIGW URL
        """
        stack_name = TestApiGateway.get_stack_name()

        client = boto3.client("cloudformation")

        try:
            response = client.describe_stacks(StackName=stack_name)
            logging.debug("Setup Stackname: %s", response)
        except Exception as error:
            raise ValueError(
                f"Cannot find stack {stack_name}. \n"
                f'Please make sure stack with the name "{stack_name}" exists.'
            ) from error

        # Setting API URL endpoints
        stack_outputs = response["Stacks"][0]["Outputs"]
        api_outputs = [
            output for output in stack_outputs if output["OutputKey"] == "APIGatewayURL"]

        self.assertTrue(
            api_outputs, f"Cannot find output APIGatewayURL in stack {stack_name}")
        self.api_endpoint = api_outputs[0]["OutputValue"]
        self.api_endpoint_inbox = self.api_endpoint + "/inbox"
        self.api_endpoint_outbox = self.api_endpoint + "/outbox"

        logging.info("Setup APIGatewayURL: %s", self.api_endpoint)
        logging.info("Setup APIGatewayURL: %s", self.api_endpoint_inbox)
        logging.info("Setup APIGatewayURL: %s", self.api_endpoint_outbox)

        # Create a random postfix for the id's to use in the message
        # Using unique id's per unit test will isolate test data
        self.id_postfix = "_" + str(uuid4())
        self.message = {
            "id": "TEST001" + self.id_postfix,
            "message": "This is a test message"
        }

    def tearDown(self) -> None:
        """
        # For tear-down, remove any data injected for the tests
        # purge Input & output SQS
        """
        # clean Input & output SQS TBD ( basicaly can be done using console UI)
        # client = boto3.client("sqs")
        # client.purge_queue(QueueUrl=self.sqs_inbox) #currently not exist
        # client.purge_queue(QueueUrl=self.sqs_outbox) # currently not exist

    def test_api_gateway_200(self):
        """
        Call the API Gateway endpoint and check the response for a 200
        """
        # Send Message to the Inbox API with Test Data
        response = requests.post(
            self.api_endpoint_inbox, json=self.message, timeout=5)
        self.assertEqual(response.status_code, 200)
        logging.info("Sent message to Inbox API: %s", self.message)

        # sleeping for 1 sec to make sure that the process lambda copies the message
        time.sleep(1)

        # Get Message from Output Queue via OUTPUT api
        response = requests.get(self.api_endpoint_outbox, timeout=5)
        self.assertEqual(response.status_code, 200)

        logging.info("Response: %s, Response code: %s",
                     response.json(), response.status_code)

        # Check if the sentmessage id is in the received message body
        self.assertIn(self.message['id'], response.json()[
                      'Messages'][0]['Body'])

    def test_api_gateway_404(self):
        """
        Call the API Gateway endpoint and check the response for a 200
        """
        
        # Get Message from Output Queue via OUTPUT api, empty Queue should return 404
        response = requests.get(self.api_endpoint_outbox, timeout=5)
        self.assertEqual(response.status_code, 404)

        logging.info("Response: %s, Response code: %s",
                     response.json(), response.status_code)

