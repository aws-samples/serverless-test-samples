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

import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { CloudFormationClient, DescribeStacksCommand, DescribeStacksCommandOutput } from '@aws-sdk/client-cloudformation';
import { KinesisClient, PutRecordsCommand } from '@aws-sdk/client-kinesis';
import { BatchWriteCommand, QueryCommand, DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
import { v4 as uuidv4 } from 'uuid';
import { UnprocessedRecord } from '../../app';

const cfClient = new CloudFormationClient({});
const ddbClient = new DynamoDBClient({});
const kinesisClient = new KinesisClient({});
const ddbDocumentClient = DynamoDBDocumentClient.from(ddbClient);

const RECORDS_STREAM_ARN_EXPORT_NAME = 'RecordsStreamArn';
const TEST_RESULTS_TABLE_EXPORT_NAME = 'RecordProcessingTestResultsTableName';

// Only wait for this long to process all records before failing
const TEST_TIMEOUT_SECONDS = 30;
const POLL_INTERVAL_SECONDS = 2;

type TestResultRecord = {
    PK: string,
    SK: string,
}

const getDeployedResources = async (): Promise<{ testTableName: string, streamArn: string }> => {
    const stackName = process.env.AWS_SAM_STACK_NAME;

    if (!stackName) {
        throw new Error('Cannot find env var AWS_SAM_STACK_NAME. Please include the stack name when running integration tests.')
    }

    let response: DescribeStacksCommandOutput;

    try {
        response = await cfClient.send(new DescribeStacksCommand({
            StackName: stackName,
        }))
    } catch (ex) {
        console.error(ex);
        throw new Error(`Cannot find stack ${stackName}. Pleas make sure the stack exists.`);
    }

    const outputs = response?.Stacks[0].Outputs;

    console.log(outputs);

    const streamOutput = outputs.find((o) => o.OutputKey === RECORDS_STREAM_ARN_EXPORT_NAME);
    if (!streamOutput) {
        throw new Error(`Stack output export ${RECORDS_STREAM_ARN_EXPORT_NAME} not found`)
    }

    const resultsTableOutput = outputs.find((o) => o.OutputKey === TEST_RESULTS_TABLE_EXPORT_NAME);
    if (!resultsTableOutput) {
        throw new Error(`Stack output export ${TEST_RESULTS_TABLE_EXPORT_NAME} not found`)
    }

    return {
        streamArn: streamOutput.OutputValue,
        testTableName: resultsTableOutput.OutputValue,
    };
}

const createMockRecordsBatch = (count: number, batchId: string): UnprocessedRecord[] => {
    const records: UnprocessedRecord[] = []

    for (let i = 0; i < count; i++) {
        const recordId = uuidv4();
        records.push({
            batch: batchId,
            id: recordId,
        })
    }

    return records;
};

const storeBatchInTable = async (records: TestResultRecord[], tableName: string): Promise<void> => {
    const writeCommand = new BatchWriteCommand({
        RequestItems: {
            [tableName]: records.map((r) => ({
                PutRequest: { Item: r }
            })),
        },
    });
    try {
        const response = await ddbDocumentClient.send(writeCommand);
        console.log(response)
    } catch (e) {
        console.error(e);
    }
};

const populateTestResultsTable = async (
    records: UnprocessedRecord[],
    tableName: string,
): Promise<void> => {
    let itemBatch : TestResultRecord[] = [];
    const batchPromises: Promise<void>[] = [];

    for (let index = 0; index < records.length; index++) {
        const item = {
            PK: records[index].batch,
            SK: `UNPROCESSED#${records[index].id}`,
        };
        itemBatch.push(item);
        const isLastItem = index === records.length - 1;

        // DDB BatchWriteItem is limited to 25 items
        if (isLastItem || itemBatch.length === 25) {
            batchPromises.push(storeBatchInTable(itemBatch, tableName));
            itemBatch = [];
        }
    }

    await Promise.all(batchPromises);
};

const sendBatchToKineses = async (
    records: UnprocessedRecord[],
    kinesisArn: string,
): Promise<void> => {
    const command = new PutRecordsCommand({
        Records: records.map((r) => ({
            PartitionKey: r.batch,
            Data: new TextEncoder().encode(JSON.stringify(r)),
        })),
        StreamARN: kinesisArn,
    });

    await kinesisClient.send(command);
};

const sendRecordsToKinesis = async (
    records: UnprocessedRecord[],
    kinesisArn: string,
): Promise<void> => {
    let itemBatch : UnprocessedRecord[] = [];
    const batchPromises: Promise<void>[] = [];

    for (let index = 0; index < records.length; index++) {
        itemBatch.push(records[index]);
        const isLastItem = index === records.length - 1;

        // Kinesis put records supports up to 500 items, total 5MB but we will limit to 100
        if (isLastItem || itemBatch.length === 100) {
            batchPromises.push(sendBatchToKineses(itemBatch, kinesisArn));
            itemBatch = [];
        }
    }

    await Promise.all(batchPromises);
};

const verifyAllResultsProcessed = async (testTableName: string, batchId: string): Promise<boolean> => {
    const startTime = performance.now();

    let completed = false;

    while (!completed && (TEST_TIMEOUT_SECONDS * 1000 + TEST_TIMEOUT_SECONDS) > performance.now()) {
        const command = new QueryCommand({
            TableName: testTableName,
            Limit: 1,
            ProjectionExpression: 'PK, SK',
            KeyConditionExpression: 'PK = :pk AND begins_with(SK, :prefix)',
            ExpressionAttributeValues: {
                ':pk': batchId,
                ':prefix': 'UNPROCESSED#',
            }
        });

        const response = await ddbClient.send(command);

        if (response.Count === 0) {
            completed = true;
        } else {
            await new Promise(res => setTimeout(res, POLL_INTERVAL_SECONDS * 1000));
        }
    }

    return completed;
}

describe('Unit test for app handler', function () {

    it('verify that the kinesis records were stored in the Dynamo DB', async () => {
        const batchId = uuidv4();

        const deployedResources = await getDeployedResources();
        const recordsBatch = createMockRecordsBatch(20, batchId);
        await populateTestResultsTable(recordsBatch, deployedResources.testTableName);

        await sendRecordsToKinesis(recordsBatch, deployedResources.streamArn);

        const completed = await verifyAllResultsProcessed(deployedResources.testTableName, batchId);

        expect(completed).toBe(true);
    }, (TEST_TIMEOUT_SECONDS + 10) * 1000);
});