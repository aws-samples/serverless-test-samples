//Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
//SPDX-License-Identifier: MIT-0

/**
 * Integration Tests
 * Before running this we would deploy the stack
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
const DATA_TABLE_EXPORT_NAME = 'ProcessedRecordsTableName';

// Only wait for this long to process all records before failing
const SUT_PROCESSING_TIMEOUT_SECONDS = 30;
const POLL_INTERVAL_SECONDS = 2;
const TEST_SETUP_CLEANUP_TIMEOUT = 30

type TestResultRecord = {
    PK: string,
    SK: string,
}

type DeployedResources = {
    testTableName: string,
    dataTableName: string,
    streamArn: string
}

let deployedResources: DeployedResources;

const getDeployedResources = async (): Promise<DeployedResources> => {
    // get the required ENV variable
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
    const streamOutput = outputs.find((o) => o.OutputKey === RECORDS_STREAM_ARN_EXPORT_NAME);
    if (!streamOutput) {
        throw new Error(`Stack output export ${RECORDS_STREAM_ARN_EXPORT_NAME} not found`)
    }

    const dataTableOutput = outputs.find((o) => o.OutputKey === DATA_TABLE_EXPORT_NAME);
    if (!dataTableOutput) {
        throw new Error(`Stack output export ${DATA_TABLE_EXPORT_NAME} not found`)
    }

    const resultsTableOutput = outputs.find((o) => o.OutputKey === TEST_RESULTS_TABLE_EXPORT_NAME);
    if (!resultsTableOutput) {
        throw new Error(`Stack output export ${TEST_RESULTS_TABLE_EXPORT_NAME} not found`)
    }

    return {
        streamArn: streamOutput.OutputValue,
        testTableName: resultsTableOutput.OutputValue,
        dataTableName: dataTableOutput.OutputValue,
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
        await ddbDocumentClient.send(writeCommand);
    } catch (e) {
        console.error(e);
    }
};

const populateTestResultsTable = async (
    records: UnprocessedRecord[],
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
            batchPromises.push(storeBatchInTable(itemBatch, deployedResources.testTableName));
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
): Promise<void> => {
    let itemBatch : UnprocessedRecord[] = [];
    const batchPromises: Promise<void>[] = [];

    for (let index = 0; index < records.length; index++) {
        itemBatch.push(records[index]);
        const isLastItem = index === records.length - 1;

        // Kinesis put records supports up to 500 items, total 5MB but we will limit to 100
        if (isLastItem || itemBatch.length === 100) {
            batchPromises.push(sendBatchToKineses(itemBatch, deployedResources.streamArn));
            itemBatch = [];
        }
    }

    await Promise.all(batchPromises);
};

const verifyAllResultsProcessed = async (
    batchId: string,
): Promise<boolean> => {
    const startTime = performance.now();

    let completed = false;

    // keep polling the test results DDB table to check if all records were processed
    while (!completed && (SUT_PROCESSING_TIMEOUT_SECONDS * 1000 + startTime) > performance.now()) {
        // query to see if unprocessed record for a batch still exists
        const command = new QueryCommand({
            TableName: deployedResources.testTableName,
            Limit: 1,
            ProjectionExpression: 'PK, SK',
            KeyConditionExpression: 'PK = :pk AND begins_with(SK, :prefix)',
            ExpressionAttributeValues: {
                ':pk': batchId,
                ':prefix': 'UNPROCESSED#',
            },
        });

        const response = await ddbClient.send(command);

        // if there isn't any unprocessed record for a batch, all records from this test were processed
        if (response.Count === 0) {
            completed = true;
        } else {
            await new Promise(res => setTimeout(res, POLL_INTERVAL_SECONDS * 1000));
        }
    }

    return completed;
}

const cleanUpTable = async (batchId: string, tableName: string): Promise<void> => {
    let exclusiveStartKey: Record<string, any> | undefined;
    const keys = [];

    // fetch all items in the batch
    do {
        const command = new QueryCommand({
            TableName: tableName,
            ProjectionExpression: 'PK, SK',
            KeyConditionExpression: 'PK = :pk',
            ExpressionAttributeValues: {
                ':pk': batchId,
            },
            ExclusiveStartKey: exclusiveStartKey,
        });
        const response = await ddbClient.send(command);
        response.Items.forEach((i) => keys.push(i));

    } while(!!exclusiveStartKey);

    // delete all items in the batch using the keys
    let deleteBatch = [];
    for (let index = 0; index < keys.length; index++) {
        deleteBatch.push({
            DeleteRequest: { Key: keys[index] },
        });
        const isLastItem = index === keys.length - 1;
        if (isLastItem || deleteBatch.length === 24) {
            const writeCommand = new BatchWriteCommand({
                RequestItems: {
                    [tableName]: deleteBatch,
                },
            });
            await ddbClient.send(writeCommand);
            deleteBatch = [];
        }
    }
};

describe('Integration test for the SUT', function () {
    beforeAll(async () => {
        deployedResources = await getDeployedResources();
    });

    it('verify that batch of 20 streamed records were stored in the Dynamo DB', async () => {
        // set up resources for this test
        const batchId = uuidv4();
        const recordsBatch = createMockRecordsBatch(20, batchId);
        await populateTestResultsTable(recordsBatch);

        // stream records to SUT
        await sendRecordsToKinesis(recordsBatch);

        // wait for completion
        const completed = await verifyAllResultsProcessed(batchId);

        // clean up
        await Promise.all([
            cleanUpTable(batchId, deployedResources.dataTableName),
            cleanUpTable(batchId, deployedResources.testTableName),
        ]);

        // verify result
        expect(completed).toBe(true);
    }, (SUT_PROCESSING_TIMEOUT_SECONDS + TEST_SETUP_CLEANUP_TIMEOUT) * 1000);

    it('verify that batch of 200 streamed ecords were stored in the Dynamo DB', async () => {
        // set up resources for this test
        const batchId = uuidv4();
        const recordsBatch = createMockRecordsBatch(200, batchId);
        await populateTestResultsTable(recordsBatch);

        // stream records to SUT
        await sendRecordsToKinesis(recordsBatch);

        // wait for completion
        const completed = await verifyAllResultsProcessed(batchId);

        // clean up
        await Promise.all([
            cleanUpTable(batchId, deployedResources.dataTableName),
            cleanUpTable(batchId, deployedResources.testTableName),
        ]);

        // verify result
        expect(completed).toBe(true);
    }, (SUT_PROCESSING_TIMEOUT_SECONDS + TEST_SETUP_CLEANUP_TIMEOUT) * 1000);
});