# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import json
import time
import binascii
import logging
from unittest import TestCase

import boto3
from botocore.config import Config
import aws_iatk


LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

class TestTrace(TestCase):
    """
    Test case to validate that our plugin (which runs in response to the 
    video system's "postvalidate" event) integrates with the proper nodes.

    Uses the Integrated Application Test Kit to pull an execution trace from
    AWS X-Ray.

    Expects two environment variables:
    PLUGIN_TESTER_STACK_NAME: the name of the stack that defines video system
    AWS_REGION: the AWS region in which the video system stack is deployed

    Note that this test method tightly couples your test code to your system
    code, which can make your tests brittle. With this we can check that the
    request hops through exactly the services we want it to. But, every time
    the path(s) change, we have to come back to the test to update it.
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
        # means we can use the Integrated Application Test Kit's ability to 
        # fetch stack outputs, fetching multiple values in a single call.
        #
        # If we didn't control the stack of the System Under Test, we might
        # have to fetch the stack outputs individually, using the 
        # Integrated Application Test Kit's ability to fetch the pysical ids
        # for stack resources
        stack_outputs = self.iatk_client.get_stack_outputs(
            stack_name=self.plugin_tester_stack_name,
            output_names=[
                "PluginLifecycleWorkflow",
                "PluginSuccessEventRuleName",
            ],
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

    def get_trace_id(self):
        """
        Generate a well-formed trace id for X-Ray
        """
        START_TIME = time.time()
        HEX=hex(int(START_TIME))[2:]
        TRACE_ID="1-{}-{}".format(HEX, binascii.hexlify(os.urandom(12)).decode('utf-8'))
        return TRACE_ID

    def get_trace_header(self, trace_id):
        """
        Format a trace id as a trace header
        """
        return "Root=" + trace_id + ";Sampled=1"

    def test_postvalidate_event_flow(self):
        """
        Test the postvalidate event plugin via the plugin tester.

        Start a plugin tester execution, which puts the trigger
        event on the default event bus. The plugin will do its work
        then should emit its own event on the default event bus.

        Once the test is complete, pull the trace to validate how the event
        was processed.
        """

        # Arrange:
        ## Note: our listener was attached during setUp().
        ## Prepare our trigger event. If this was registered in the EventBridge
        ## Schema Registry, we could use the Integrated Application Test Kit 
        ## to generate it.
        trace_id = self.get_trace_id()
        trace_header = self.get_trace_header(trace_id)
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
            traceHeader=trace_header,
            input=json.dumps(trigger_event)
        )

        # Wait for the trace to populate
        # You can consider 'retry_get_trace_tree_until' here
        time.sleep(20)

        # Assert:
        ## Pull the trace from AWS X-Ray and validate
        trace_tree = self.iatk_client.get_trace_tree(
            tracing_header=trace_header,
        ).trace_tree

        # Assert that we only have one trace path 
        # and it has the right number of segments
        self.assertEqual(len(trace_tree.paths), 1)
        self.assertEqual(len(trace_tree.paths[0]), 6)

        # Set up the expected segments this request hops through
        # as Segment origin / Segment name tuples
        expected_origin_name_segments = [
            ('AWS::StepFunctions::StateMachine','PluginLifecycleWorkflow'),
            ('AWS::Events','Events'),
            ('AWS::Lambda','PythonMinimalPluginFunction'),
            ('AWS::Lambda::Function','PythonMinimalPluginFunction'),
            ('AWS::Lambda','PluginTaskSuccessFunction'),
            ('AWS::Lambda::Function','PluginTaskSuccessFunction'),
        ]
        for i,segment in enumerate(trace_tree.paths[0]):
            # If this segment has an error or fault, fail
            self.assertIsNone(segment.error)
            self.assertIsNone(segment.fault)

            # If this segment isn't the right service or resource, fail
            self.assertEqual(expected_origin_name_segments[i][0], segment.origin)
            self.assertIn(expected_origin_name_segments[i][1], segment.name)