//Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
//SPDX-License-Identifier: MIT-0

/**
 * Integration Tests
 * Before running this we would deploy the stack 
 * 
*/

import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import {
  DynamoDBDocumentClient,
  DeleteCommand,
  GetCommandInput,
  GetCommand
} from "@aws-sdk/lib-dynamodb";
import { eventJSON } from "../../src/events/event-data";
import { lambdaHandler } from "../../src/app";

const dynamodb = new DynamoDBClient({});
const ddb = DynamoDBDocumentClient.from(dynamodb);

async function deleteItem(id: string): Promise<void> {
  const deleteParam = { Key: { 'ID': id }, TableName: process.env.DatabaseTable };
  await ddb.send(new DeleteCommand(deleteParam));
}

describe('Lambda and DynamoDB Integration test', () => {

  /**
   * Note have an entry in the database with id 1. 
   * If the entry is not there the test case would fail for the first time.
   */
  describe('Lambda handler', () => {
    it('should put an item in the dynamodb table', async () => {

      const TEST_ITEM_ID:string = eventJSON.Records[0].eventID as string;
      const result: any = await lambdaHandler(eventJSON);

      // Assert that the response from the Lambda handler is successful
      expect(result.statusCode).toBe(200);

      //Retrieve the item from the DynamoDB table
      const params: GetCommandInput = {
        TableName: process.env.DatabaseTable,
        Key: { 'ID': TEST_ITEM_ID }
      };
      const response = await ddb.send(new GetCommand(params));

      // Assert that the item was successfully found in the DynamoDB table
      expect(response).toBeDefined();
      expect(response.Item?.ID).toBe(TEST_ITEM_ID);
    
      // Clean up the item
      await deleteItem(TEST_ITEM_ID);
    });
  });
});