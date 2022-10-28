// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { S3Client, ListBucketsCommand } from '@aws-sdk/client-s3';

const region = process.env.AWS_REGION ?? 'us-east-1';
const s3Client = new S3Client({ region: region });

/**
 *
 * Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format
 * @param {Object} event - API Gateway Lambda Proxy Input Format
 *
 * Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
 * @returns {Object} object - API Gateway Lambda Proxy Output Format
 *
 */
export const lambdaHandler = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
    try {
        console.log('Called with event', event);

        const listBucketsOutput = await s3Client.send(new ListBucketsCommand({}));
        let bucketList = '';
        if (listBucketsOutput.Buckets) {
            bucketList = listBucketsOutput.Buckets?.map((bucket) => bucket.Name).join(' | ');
        }
        console.log('Bucket list created');

        return {
            statusCode: 200,
            body: bucketList,
        };
    } catch (error) {
        console.error('Error', error);
        return {
            statusCode: 500,
            body: '',
        };
    }
};
