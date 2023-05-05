//Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
//SPDX-License-Identifier: MIT-0

/**
 * Lambda Handler for the typescript pattern lambda-handler-dynamodb
 * This handler put a new item in the DynamoDB table using AWS SDK.
 * The DynamoDB Table used is passed as an environment variable "DatabaseTable"
*/

import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { PutCommand, DynamoDBDocumentClient } from "@aws-sdk/lib-dynamodb";
import { DynamoDBStreamEvent } from "aws-lambda/trigger/dynamodb-stream";
import moment = require('moment');

const dynamodb = new DynamoDBClient({});
const ddb = DynamoDBDocumentClient.from(dynamodb);

export const lambdaHandler = async ( event: DynamoDBStreamEvent ) => {
  try {
    const params = {
      TableName : process.env.DatabaseTable,
      Item: {
        ID: event.Records[0].eventID,
        created: moment().format('YYYYMMDD-hhmmss'),
        metadata: JSON.stringify(event),
      }
    }

    await ddb.send(new PutCommand(params));
  }
  catch (err) {
    console.log(err);
    return err;
  }
  return {
    statusCode: 200,
    body: 'OK!',
  };
}