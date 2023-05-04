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

const dynamodb = new DynamoDBClient({ region: 'us-east-1' });
const ddb = DynamoDBDocumentClient.from(dynamodb);

async function deleteItem(){
    let ids = "1";             
    let deleteParam = {Key: {'ID': ids}, TableName: process.env.DatabaseTable};
    await ddb.send(new DeleteCommand(deleteParam));
}

describe('Lambda and DynamoDB Integration test', () => {
    /**
     * Shared test setup
     * In this case, we're using a afterAll block to delete an item we insert into DynamoDB table for integration test.
     * This test need an item in DynamoDB table to check if Lambda handler can integrate with DynamoDB.
     */

    afterAll( async () =>{
       await deleteItem();
    })

    /**
     * Note have an entry in the database with id 1. 
     * If the entry is not there the test case would fail for the first time.
     */
    describe('Lambda handler', () => {
        it('should put an item in the dynamodb table', async () => {
            const result: any = await lambdaHandler(eventJSON);
            
            // Assert that the response from the Lambda handler is successful
            expect(result.statusCode).toBe(200);
        
            //Retrieve the item from the DynamoDB table
            const params: GetCommandInput = {
                TableName: process.env.DatabaseTable,
                Key: {"ID": "1"}
            };
            const response = await ddb.send(new GetCommand(params));
        
            // Assert that the item was successfully found in the DynamoDB table
            expect(response).toBeDefined();
            expect(response.Item?.ID).toBe("1");
        });
    });
});