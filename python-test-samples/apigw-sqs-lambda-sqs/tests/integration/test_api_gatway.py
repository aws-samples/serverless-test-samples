"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

Set the environment variable AWS_SAM_STACK_NAME to the name of the stack you deploied
>>> export AWS_SAM_STACK_NAME=<stack-name> 
>>> python -m pytest -s tests/integration -v
or run the following to see also log info messages  
>>> python -m pytest -s tests/integration --log-cli-level=20
"""

import os
import time
import logging
from unittest import TestCase
from uuid import uuid4
from boto3.dynamodb.conditions import Key
import boto3
import requests

logging.basicConfig(level=logging.INFO)

class TestApiGateway(TestCase):
    """THe main test class for the API Gateway"""
    api_endpoint: str
    api_endpoint_inbox: str
    api_endpoint_outbox: str
    sqs_input: str
    sqs_output: str
    sqs_input_dlq: str
    sqs_output_dlq: str

    service_level_agreement = 20
    # number of times to check if there is a message in the queue (can't be 0)
    interval_num = 5
    # amount of time to wait between each check
    interval_timeout = int(service_level_agreement/interval_num)

    sleep_interval = 10 # for simple sleep usecases

    aws_region = os.environ.get("AWS_DEFAULT_REGION") or "us-east-1"

    # Create a random postfix for the id's to use in the message
    # Using unique id's per unit test will isolate test data
    id_postfix = "_" + str(uuid4())
    test_time = time.strftime("%H:%M:%S", time.localtime())

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

        cf_client = boto3.client("cloudformation")

        try:
            response = cf_client.describe_stacks(StackName=stack_name)
            #logging.info("Setup Stackname: %s", response)
        except Exception as error:
            raise ValueError(
                f"Cannot find stack {stack_name}. \n"
                f'Please make sure stack with the name "{stack_name}" exists.'
            ) from error

        # setting endpoints
        stack_outputs = response["Stacks"][0]["Outputs"]
        api_outputs = [
            output for output in stack_outputs if output["OutputKey"] == "APIGatewayURL"]
        sqs_input = [
            output for output in stack_outputs if output["OutputKey"] == "SQSInputQueue"]
        sqs_output = [
            output for output in stack_outputs if output["OutputKey"] == "SQSOutputQueue"]
        sqs_input_dlq = [
            output for output in stack_outputs if output["OutputKey"] == "SQSInputQueueDLQ"]
        sqs_output_dlq = [
            output for output in stack_outputs if output["OutputKey"] == "SQSOutputQueueDLQ"]
        dynamodb_outputs = [
            output for output in stack_outputs if output["OutputKey"] == "DynamoDBTableName"]

        self.api_endpoint = api_outputs[0]["OutputValue"]
        self.api_endpoint_inbox = self.api_endpoint + "/inbox"
        self.api_endpoint_outbox = self.api_endpoint + "/outbox"
        self.sqs_input = sqs_input[0]["OutputValue"]
        self.sqs_output = sqs_output[0]["OutputValue"]
        self.sqs_input_dlq = sqs_input_dlq[0]["OutputValue"]
        self.sqs_output_dlq = sqs_output_dlq[0]["OutputValue"]
        self.dynamodb_table_name = dynamodb_outputs[0]["OutputValue"]

        logging.info("Setup APIGatewayURL: %s", self.api_endpoint)
        logging.info("Setup APIGatewayURL_Inbox: %s", self.api_endpoint_inbox)
        logging.info("Setup APIGatewayURL_Outbox: %s", self.api_endpoint_outbox)
        logging.info("Setup SQSInputQueue: %s", self.sqs_input)
        logging.info("Setup SQSOutputQueue: %s", self.sqs_output)
        logging.info("Setup SQSInputQueueDLQ: %s", self.sqs_input_dlq)
        logging.info("Setup SQSOutputQueueDLQ: %s", self.sqs_output_dlq)
        logging.info("Setup DynamoDBTable: %s", self.dynamodb_table_name)

        # Seed the DynamoDB Table with Test Data
        self.dynamodb_resource = boto3.resource("dynamodb", region_name = self.aws_region)
        self.dynamodb_table = self.dynamodb_resource.Table(name=self.dynamodb_table_name)

        # The following item, just a samole, and will be deleted in teardown #
        # self.dynamodb_table.put_item(Item={"id": "TEST000" + self.id_postfix,
        #                               "Queue_Name": "NAME#",
        #                               "Message": self.test_time + " Init DB Record" })

    def teardown_class(self) -> None:
        """
        # For tear-down, remove any data injected for the tests
        # purge each queue in case they have messages inside them
        # since purge can be done once every 60 sec, we start with 60 sec sleep
        """
        logging.info("Teardown Phase...")
        
        # Take particular care to ensure these values are unique and identifiable as TEST data.
        logging.info("Teardown DynamoDB...")

        for test_id in ["TEST000", "TEST001" ,"TEST002", "TEST003"]:
            message_id = test_id + self.id_postfix
            id_items = self.dynamodb_table.query(
                KeyConditionExpression=Key('id').eq(message_id))

            if "Items" in id_items:
                for item in id_items["Items"]:
                    self.dynamodb_table.delete_item(Key={"id":item["id"]})

        # cleaning SQS queues
        logging.info("Teardown SQS...")

        client = boto3.client("sqs")
        response = {}

        response = client.get_queue_attributes(
            QueueUrl=self.sqs_input,
            AttributeNames=['ApproximateNumberOfMessages']
        )

        message_count = int(response['Attributes']
                            ['ApproximateNumberOfMessages'])
        if message_count > 0:
            logging.info("Cleaning input queue")
            client.purge_queue(QueueUrl=self.sqs_input)  # purging input queue

        response = client.get_queue_attributes(
            QueueUrl=self.sqs_output,
            AttributeNames=['ApproximateNumberOfMessages']
        )

        message_count = int(response['Attributes']
                            ['ApproximateNumberOfMessages'])
        if message_count > 0:
            logging.info("Cleaning output queue")       # purging output queue
            client.purge_queue(QueueUrl=self.sqs_output)

        response = client.get_queue_attributes( QueueUrl=self.sqs_input_dlq,
            AttributeNames=['ApproximateNumberOfMessages']
        )

        message_count = int(response['Attributes']['ApproximateNumberOfMessages'])
        if message_count > 0:
            logging.info("Cleaning input DLQ")          # purging inputDLQ queue
            client.purge_queue(QueueUrl=self.sqs_input_dlq)

        response = client.get_queue_attributes(QueueUrl=self.sqs_output_dlq,
            AttributeNames=['ApproximateNumberOfMessages']
        )

        message_count = int(response['Attributes']['ApproximateNumberOfMessages'])
        if message_count > 0:
            logging.info("Cleaning output DLQ")         # purging output DLQ
            client.purge_queue(QueueUrl=self.sqs_output_dlq)
        response = client.get_queue_attributes(
            QueueUrl=self.sqs_input,
            AttributeNames=['ApproximateNumberOfMessages']
        )

    def test_positive_scenario(self):
        """
        This is a positive test to verify that a valid message is going all the way to the output queue
        Call the API Gateway endpoint and check the response for a 200
        If the result is 200, check in the DynamoDB that the message arrived properly
        """
        # Send Message to the Inbox API with Test Data, SQS SLA is 5 seconds

        message_id = "TEST001" + self.id_postfix
        message_text = self.test_time + " This is a test_positive_scenario"
        message = {
            "id": message_id,
            "message": message_text
        }

        response = requests.post(
            self.api_endpoint_inbox, json=message, timeout=5)
        self.assertEqual(response.status_code, 200)
        logging.info("Sent message to Inbox API: %s", message)

         # we sleep sleep interval before checking the DB and Queues
        time.sleep(self.sleep_interval)

        id_items = self.dynamodb_table.query(
                KeyConditionExpression=Key('id').eq(message_id))
        # Check that DynamoDB received the relevant message and from the relevant Queue
        self.assertEqual(id_items["Count"], 1, "DB did not receive the message, Hint: check your sleep interval")
        self.assertEqual(id_items["Items"][0]["Message"], message_text, "Wrong message received")
        sqs_output = self.sqs_output.split("/")[-1] 
        db_queue_name = id_items["Items"][0]["Queue_Name"].split(":")[-1]
        self.assertEqual(db_queue_name, sqs_output, "Wrong Queue name.")

        # # looping for the number of times to check if there is a message in the quque
        # msg_found = False
        # for i in range(self.service_level_agreement):
        #     # Get Message from Output Queue via OUTPUT api
        #     logging.info ("Checking for message in the output queue %s time out of %s"\
        #             ,i+1, self.service_level_agreement)
        #     response = requests.get(self.api_endpoint_outbox, timeout=self.interval_timeout)
        #     if response.status_code == 200:
        #         msg_found = True
        #         # Check if the sentmessage id is in the received message body
        #         self.assertIn(message['id'],
        #                       response.json()['Messages'][0]['Body'])
        #         logging.info("Response: %s, Response code: %s",
        #                      response.json(), response.status_code)
        #         break

        #     # Sleep for interval_timeout before checking again
        #     logging.info("Sleeping for %s seconds before checking again", self.interval_timeout)
        #     time.sleep(self.interval_timeout)

        #     # Check if message was found in the output queue or raise fail test
        #     if (i == self.interval_num - 1) and (not msg_found):
        #         logging.info("Message was not found in the output queue")
        #         self.fail("Message was not found in with in the SLA {self.service_level_agreement}")

    def test_false_positive_scenario(self):
        """
        This is a false positive test to verify that a valid message is going all the way to the output queue
        Call the API Gateway endpoint and check the response for a 200
        If the result is 200, check in the DynamoDB that the message arrived properly
        """
        # Send Message to the Inbox API with Test Data, SQS SLA is 5 seconds

        message_id = "TEST002" + self.id_postfix
        message_text = self.test_time + " This is a test_false_positive_scenario"
        message = {
            "id": message_id,
            "message": message_text
        }

        response = requests.post(
            self.api_endpoint_inbox, json=message, timeout=5)
        self.assertEqual(response.status_code, 200)
        logging.info("Sent message to Inbox API: %s", message)

         # we sleep sleep interval before checking the DB and Queues
        time.sleep(self.sleep_interval)

        id_items = self.dynamodb_table.query(
                KeyConditionExpression=Key('id').eq(message_id))
        # Check that DynamoDB received the relevant message and from the relevant Queue
        self.assertEqual(id_items["Count"], 1, "DB did not receive the message, Hint: check your sleep interval")
        sqs_output = self.sqs_output.split("/")[-1] 
        self.assertEqual(id_items["Items"][0]["Message"], message_text, "Wrong message received.")
        db_queue_name = id_items["Items"][0]["Queue_Name"].split(":")[-1]
        self.assertEqual(db_queue_name, sqs_output, "Wrong Queue name.")


    def test_exception_scenario(self):
        """
        This test simulate unexpected exception in the process lambda (SUT)
        The funciton create a mallform message and send it to the APIGW,
        The Process Lambda will raise error exception and won't process the message, 
        hence the Queue will move the message to DLQ.
        The test will check the DLQ to see if a message was received
        """
        #response = {}

        message_id = "TEST003" + self.id_postfix
        message_text = self.test_time + " MALFORMED_MASSAGE - this is a test_exception_scenario"
        message = {
            "id": message_id,
            "message": message_text
        }

        # Send Message to the Inbox API with Test Data, SQS SLA is 5 seconds
        response = requests.post(
            self.api_endpoint_inbox, json=message, timeout=5)
        self.assertEqual(response.status_code, 200)
        logging.info("Sent message to Inbox API: %s", message)

        # we sleep sleep interval before checking the DB and Queues
        time.sleep(self.sleep_interval)

        id_items = self.dynamodb_table.query(
                KeyConditionExpression=Key('id').eq(message_id))
        self.assertEqual(id_items["Count"], 1, "DB did not receive the message, Hint: check your sleep interval")
        self.assertEqual(id_items["Items"][0]["Message"], message_text)

        # in this test we expect that the message will arrive from input DLQ to the DynamoDB.
        sqs_output = self.sqs_input_dlq.split("/")[-1] 
        db_queue_name = id_items["Items"][0]["Queue_Name"].split(":")[-1]
        self.assertEqual(db_queue_name, sqs_output,  "Wrong Queue name.")


        # # Check the Dealetter input Queue for any messages
        # # Process_input_lambda should deny, and then SQS will move the message to the DLQ
        # for i in range(self.service_level_agreement):
        #     logging.info("\nChecking for message in the DL queue %s time out of %s"\
        #                  ,i+1, self.service_level_agreement)
        #     response = client.get_queue_attributes(
        #         QueueUrl=self.sqs_input_dlq,
        #         AttributeNames=['ApproximateNumberOfMessages']
        #     )
        #     message_count = int(response['Attributes']
        #                         ['ApproximateNumberOfMessages'])
        #     if message_count > 0:
        #         self.assertGreater(message_count, 0)
        #         break

        #     time.sleep(self.interval_timeout)

        # self.assertGreater(message_count, 0)
