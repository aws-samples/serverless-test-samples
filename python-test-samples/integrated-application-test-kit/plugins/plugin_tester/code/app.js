//Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
//SPDX-License-Identifier: MIT-0

const { SFNClient, SendTaskSuccessCommand } = require('@aws-sdk/client-sfn');
const stepfunctions = new SFNClient();

exports.handler = async (event) => {
  try {
    // Extract the required input from the EventBridge event
    const input = event.detail.Message;

    // Replace this with your Step Functions state machine ARN
    const stateMachineArn = process.env.PluginLifecycleWorkflow;

    // Send the task success with the input to the Step Functions state machine
    const params = {
      taskToken: event.detail['TaskToken'],
      output: JSON.stringify(input),
    };

    await stepfunctions.send(new SendTaskSuccessCommand(params));

    console.log('Task success sent to Step Functions.');

    return {
      statusCode: 200,
      body: JSON.stringify({ message: 'Task success sent to Step Functions.' }),
    };
  } catch (error) {
    console.error('Error:', error);

    return {
      statusCode: 500,
      body: JSON.stringify({ message: 'Error sending task success to Step Functions.' }),
    };
  }
};
