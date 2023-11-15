//Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
//SPDX-License-Identifier: MIT-0

const { EventBridgeClient, PutEventsCommand } = require("@aws-sdk/client-eventbridge");

exports.lambdaHandler = async (event, context) => {

    // Do some stuff here and validate that you've been successful
    let valid = {
        "valid": true,
        "reason": "The plugin works!"
    };

    // Extract duration and taskToken from the incoming event
    var taskToken = event["detail"]["taskToken"];

    // Configure the EventBridge client
    const eventBridgeClient = new EventBridgeClient();

    const eventToSend = { 
        Entries: [ 
          { 
            Source: 'video.plugin.TestPlugin',
            DetailType: 'plugin-complete',
            EventBusName: "default",
            Detail: JSON.stringify({"TaskToken": taskToken,"Message":valid})
          },
        ]
      };

    try {
        // Put the event on EventBridge
        const command = new PutEventsCommand(eventToSend);
        await eventBridgeClient.send(command);
        return {
            statusCode: 200,
            body: "Success!"
        };
      } catch (error) {
        console.error('Error sending event:', error);
        return {
            statusCode: 500,
            body:'Error sending event.'
        }
      }   
}
