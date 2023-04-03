//Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
//SPDX-License-Identifier: MIT-0

/**
 * Lambda Handler for the typescript kinesis-lambda-dynamodb
 * This handler accepts a kinesis event with records that contain JSON object in data property
 * The DynamoDB Table used is passed as an environment variable "PROCESSED_RECORDS_TABLE_NAME"
*/

import { KinesisStreamEvent, KinesisStreamRecord } from 'aws-lambda';
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import {
    BatchWriteCommand,
    DynamoDBDocumentClient,
} from "@aws-sdk/lib-dynamodb";

const ddbClient = new DynamoDBClient({});
const ddbDocumentClient = DynamoDBDocumentClient.from(ddbClient);

type ProcessedRecord = {
  PK: string,
  SK: string,
}

export const lambdaHandler = async (event: KinesisStreamEvent): Promise<void> => {
    // Getting the dynamoDB table name from environment variable
    const dynamoDBTableName = process.env.PROCESSED_RECORDS_TABLE_NAME;

    let itemBatch : ProcessedRecord[] = [];
    const batchPromises: Promise<void>[] = [];

    for (let index = 0; index < event.Records.length; index++) {
        const item = createRecordItem(event.Records[index]);
        itemBatch.push(item);
        const isLastItem = index === event.Records.length - 1;

        // DDB BatchWriteItem is limited to 25 items
        if (isLastItem || itemBatch.length === 25) {
            batchPromises.push(storeBatchInTable(itemBatch, dynamoDBTableName));
            itemBatch = [];
        }
    }

    await Promise.all(batchPromises);
};

const createRecordItem = (record: KinesisStreamRecord): ProcessedRecord => {
    const payload = Buffer.from(record.kinesis.data, 'base64').toString('ascii');
    const data = JSON.parse(payload);

    return {
        'PK': data.batch,
        'SK': data.id,
    };
}

const storeBatchInTable = async (records: ProcessedRecord[], tableName: string): Promise<void> => {
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