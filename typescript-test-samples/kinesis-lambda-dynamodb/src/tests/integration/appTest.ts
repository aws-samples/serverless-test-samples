//Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
//SPDX-License-Identifier: MIT-0

/**
 * Lambda Handler for the typescript kinesis-lambda-dynamodb testing listener
 * This handler accepts a dynamo stream event to process the test results
*/

import { DynamoDBStreamEvent } from 'aws-lambda';


export const lambdaHandler = async (event: DynamoDBStreamEvent): Promise<void> => {
    // Getting the dynamoDB table name from environment variable
    console.log(event);
};
