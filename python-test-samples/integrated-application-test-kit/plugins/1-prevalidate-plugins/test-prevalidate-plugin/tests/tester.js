//Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
//SPDX-License-Identifier: MIT-0

'use strict';

const app = require('../functions/app.js');
const chai = require('chai');
const { v4: uuidv4 } = require('uuid');
const expect = chai.expect;
const { CloudFormationClient, DescribeStacksCommand } = require("@aws-sdk/client-cloudformation");
const { SFNClient, StartExecutionCommand, DescribeExecutionCommand } = require("@aws-sdk/client-sfn");
const fs = require('fs');
const context = "";
const stack = process.env.PLUGIN_TESTER_STACK_NAME;
const sfn_client = new SFNClient({ region: process.env.AWS_REGION });

try {
  var valid_event = fs.readFileSync('./events/valid_event.json', 'utf8');
} catch (err) {
  console.error(err);
}

describe('Run unit tests for TestPlugin', function () {
  it('test Lambda function handler', async () => {
    const result = await app.lambdaHandler(JSON.parse(valid_event), context)
    expect(result).to.be.an('object');
    expect(result.statusCode).to.equal(200);
    expect(result.body).to.be.an('string');
    let response = result.body;
    expect(response).to.be.equal("Success!");
  });
});

describe('Run integration tests for TestPlugin', async function () {
  it('test using Step Functions test harness', async () => {
    const cfm_client = new CloudFormationClient();
    const cfm_input = { StackName: process.env.PLUGIN_TESTER_STACK_NAME };
    const cfm_command = new DescribeStacksCommand(cfm_input);
    const cfm_response = await cfm_client.send(cfm_command);
    const plugin_state_machine_arn = (cfm_response["Stacks"][0]["Outputs"][0]["OutputValue"]);
    const execution_name = "Test-TestPlugin-" + uuidv4();

    let input =
    {
      "eventHook": "preValidate",
      "pluginTitle": "TestPlugin"
    }

    let sfn_input = {
      stateMachineArn: plugin_state_machine_arn,
      name: execution_name,
      input: JSON.stringify(input)
    };

    // start the execution
    let sfn_command = new StartExecutionCommand(sfn_input);
    let response = await sfn_client.send(sfn_command);
    let executionArn = (response["executionArn"]);

    // loop until it is finished or until 30 seconds have passed
    let x = 1
    do {
      x++;
      sfn_input = {
        executionArn
      };
      sfn_command = new DescribeExecutionCommand(sfn_input);
      response = await sfn_client.send(sfn_command);
      console.log("Status: " + response["status"]);
      await sleep(2000);
      if (x >= 15) break;
    } while (response["status"] == "RUNNING");

    expect(response["status"]).to.equal("SUCCEEDED");

  }).timeout(30000); // 30 seconds is our plugin SLA

  function sleep(millis) {
    return new Promise(resolve => setTimeout(resolve, millis));
  }

});
