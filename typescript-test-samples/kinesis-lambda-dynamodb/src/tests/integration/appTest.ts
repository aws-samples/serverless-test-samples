//Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
//SPDX-License-Identifier: MIT-0

/**
 * Lambda Handler for the typescript kinesis-lambda-dynamodb testing listener
 * This handler accepts a dynamo stream event to process the test results
*/

import { DynamoDBRecord, DynamoDBStreamEvent } from 'aws-lambda';
import { AttributeValue, DynamoDBClient } from "@aws-sdk/client-dynamodb";
import {
    BatchWriteCommand,
    DynamoDBDocumentClient,
} from "@aws-sdk/lib-dynamodb";
import { unmarshall } from "@aws-sdk/util-dynamodb";

const ddbClient = new DynamoDBClient({});
const ddbDocumentClient = DynamoDBDocumentClient.from(ddbClient);

export type TestResult = {
    PK: string,
    SK: string,
}

type ProcessedRecord = {
    PK: string,
    SK: string,
}

export const lambdaHandler = async (event: DynamoDBStreamEvent): Promise<void> => {
    const dynamoDBTableName = process.env.TEST_RESULTS_TABLE_NAME;
    let itemBatch = [];
    const batchPromises: Promise<void>[] = [];

    for (let index = 0; index < event.Records.length; index++) {
        // Ignore deletion or modification events
        if (event.Records[index].eventName !== 'INSERT') continue;

        const processedRecord = unmarshallProcessedRecord(event.Records[index]);
        itemBatch.push({
            PutRequest: {
                Item: {
                    PK: processedRecord.PK,
                    SK: `PROCESSED#${processedRecord.SK}`
                },
            },
        });
        itemBatch.push({
            DeleteRequest: {
                Key: {
                    PK: processedRecord.PK,
                    SK: `UNPROCESSED#${processedRecord.SK}`
                },
            },
        });

        const isLastItem = index === event.Records.length - 1;

        // DDB BatchWriteItem is limited to 25 items, we want to process 12 pairs of put and delete
        if (isLastItem || itemBatch.length === 24) {
            batchPromises.push(processBatch(itemBatch, dynamoDBTableName));
            itemBatch = [];
        }
    }

    await Promise.all(batchPromises);
};

const unmarshallProcessedRecord = (record: DynamoDBRecord): ProcessedRecord => (
    unmarshall(
        record.dynamodb.NewImage as { [key: string]: AttributeValue },
    ) as ProcessedRecord
);

const processBatch = async (records: any[], tableName: string): Promise<void> => {
    const writeCommand = new BatchWriteCommand({
        RequestItems: {
            [tableName]: records,
        },
    });

    try {
        const response = await ddbDocumentClient.send(writeCommand);
    } catch (e) {
        console.error(e);
    }
};
