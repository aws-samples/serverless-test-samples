//Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
//SPDX-License-Identifier: MIT-0

/**
 * test-handler.test.ts
 *
 * Unit tests for the Lambda handler function.
 *
  The unit tests here are focused on testing this interface, exercising code
 * paths that validate inbound request payloads and checking for correct
 * behavior when the busines layer returns different results.
 */

/**
 * Import Modules
 *
 * Standard practice to put imports at the top of a module definition.
 *
*/

import { lambdaHandler } from '../../app';
import { mockClient } from "aws-sdk-client-mock";
import { BatchWriteCommand, DynamoDBDocumentClient } from "@aws-sdk/lib-dynamodb";
import { eventJSON } from '../../events/batch-of-five-event';
import 'aws-sdk-client-mock-jest';

const ddbMock = mockClient(DynamoDBDocumentClient);

describe('Unit test for app handler', function () {

    it('verify that the kinesis records were stored in the Dynamo DB', async () => {
        process.env.PROCESSED_RECORDS_TABLE_NAME = 'unit_test_table_name';

        ddbMock.on(BatchWriteCommand).resolves({});

        lambdaHandler(eventJSON);

        expect(ddbMock).toHaveReceivedCommand(BatchWriteCommand);

        expect(ddbMock.commandCalls(BatchWriteCommand)).toHaveLength(1);

        expect(ddbMock.commandCalls(BatchWriteCommand)[0].args[0].input.RequestItems['unit_test_table_name'])
            .toEqual(expect.arrayContaining([
                { PutRequest: { Item: { 'PK': 'e04c537a-7177-4254-afae-594470849a2d', 'SK': '0537f1b4-e439-4ed0-ab09-f327f05550ac' }}},
                { PutRequest: { Item: { 'PK': 'e04c537a-7177-4254-afae-594470849a2d', 'SK': '2734e753-6330-4658-b0d7-a9bcde4fd3a5' }}},
                { PutRequest: { Item: { 'PK': 'e04c537a-7177-4254-afae-594470849a2d', 'SK': '369c296e-5b15-4503-99c4-fd469e61bd4c' }}},
                { PutRequest: { Item: { 'PK': 'e04c537a-7177-4254-afae-594470849a2d', 'SK': '85a05bd1-147a-4872-a830-cb6c7e229e08' }}},
                { PutRequest: { Item: { 'PK': 'e04c537a-7177-4254-afae-594470849a2d', 'SK': 'd3f475d5-301c-4482-9614-2b18d45b5a45' }}},
            ]));
    });
});