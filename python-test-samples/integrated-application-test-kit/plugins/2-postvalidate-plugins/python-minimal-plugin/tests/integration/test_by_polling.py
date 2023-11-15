# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import json
from unittest import TestCase

import boto3
from botocore.config import Config
import aws_iatk

class TestMinimalPluginByPolling(TestCase):
    """
    Test case to validate that our plugin (which runs in response to the 
    video system's "postvalidate" event) emits the correct event to the
    event bus after processing.

    Uses the "polling" method to pull events from our 
    Integrated Application Test Kit listener

    Expects two environment variables:
    PLUGIN_TESTER_STACK_NAME: the name of the stack that defines video system
    AWS_REGION: the AWS region in which the video system stack is deployed
    """

    # Initialize variables from environment
    aws_region = os.environ.get("AWS_REGION")
    if(aws_region is None):
        raise Exception("AWS_REGION environment variable is required")
    plugin_tester_stack_name = os.environ.get("PLUGIN_TESTER_STACK_NAME")
    if(plugin_tester_stack_name is None):
        raise Exception("PLUGIN_TESTER_STACK_NAME environment variable is required")

    # Initialize clients
    iatk_client = aws_iatk.AwsIatk(region=aws_region)
    step_functions_client = boto3.client("stepfunctions", config=Config(region_name=aws_region))

    # Set up variables for polling
    SLA_TIMEOUT_SECONDS: int = 20
    listener_id: str = None
    plugin_tester_arn: str = None
    existing_rule_name: str = None

    def setUp(self):
        """
        Prepare context for running this test case
        """

        # Look up identifiers for cloud resources. Since we own the stack 
        # of the System Under Test, we can influence the stack outputs. This 
        # means we can use the Integrated Application Test Kit's ability to fetch stack 
        # outputs, fetching multiple values in a single call.
        #
        # If we didn't control the stack of the System Under Test, we might
        # have to fetch the stack outputs individually, using the
        # # Integrated Application Test Kit's ability to fetch the pysical ids
        # for stack resources
        stack_outputs = self.iatk_client.get_stack_outputs(
            stack_name=self.plugin_tester_stack_name,
            output_names=["PluginLifecycleWorkflow","PluginSuccessEventRuleName"],
        )
        self.plugin_tester_arn = stack_outputs.outputs["PluginLifecycleWorkflow"]
        self.existing_rule_name = stack_outputs.outputs["PluginSuccessEventRuleName"]

        # Attach a Integrated Application Test Kit listener to the correct event bus.
        # Reference the existing rule name that we looked up from the stack
        # as the rule to clone when setting up the listener.
        # Store the listener's id so we can remove it later.
        add_listener_output = self.iatk_client.add_listener(
            event_bus_name="default",
            rule_name=self.existing_rule_name
        )
        self.listener_id = add_listener_output.id

    def tearDown(self):
        """
        Clean up after running this test case
        """

        # Remove the listener that was created in setUp. This is important
        # because if we don't remove the listener, the cloned rule will remain 
        # in place. It will continue to be triggered by events hitting the bus.
        self.iatk_client.remove_listeners(
            ids=[self.listener_id]
        )

    def test_minimal_plugin_event_published_polling(self):
        """
        Test case to validate that our plugin (which runs in response to the 
        video system's "postvalidate" event) emits the correct event to the
        event bus after processing.
        """

        # Arrange:
        ## Note: our listener was attached during setUp().
        ## Prepare our trigger event. If this was registered in the EventBridge
        ## Schema Registry, we could use the Integrated Application Test Kit 
        ## to generate it.
        trigger_event = {
            "eventHook": "postValidate",
            "pluginTitle": "PythonMinimalPlugin"
        }

        # Act:
        ## Execute the plugin tester Step Function workflow, which will put the
        ## trigger event on the event bus in the same way the production video
        ## system does.
        self.step_functions_client.start_execution(
            stateMachineArn=self.plugin_tester_arn,
            input=json.dumps(trigger_event)
        )

        # Assert: 
        ## Poll the listener to watch for captured events until the SLA expires
        ## or until we receive the expected event. We're only expecting a
        ## single event because we're only triggering the plugin once.
        poll_output = self.iatk_client.poll_events(
            listener_id=self.listener_id,
            wait_time_seconds=self.SLA_TIMEOUT_SECONDS,
            max_number_of_messages=1,
        )

        # Validate that we received an event...
        self.assertEqual(len(poll_output.events), 1)

        # ... and that it was the one we expected based on the plugin contract
        received_event = json.loads(poll_output.events[0])
        self.assertEqual(received_event["source"], "video.plugin.PythonMinimalPlugin")
        self.assertEqual(received_event["detail-type"], "plugin-complete")