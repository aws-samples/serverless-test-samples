// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { listBucketsLambdaHandler } from '../../app';
import { beforeEach, beforeAll, describe, it, expect } from '@jest/globals';
import { mockClient } from 'aws-sdk-client-mock';
import { S3Client, ListBucketsCommand } from '@aws-sdk/client-s3';

let inputEvent: APIGatewayProxyEvent;

const s3Mock = mockClient(S3Client);

beforeAll(() => {
    inputEvent = {
        httpMethod: 'get',
        body: '',
        headers: {},
        isBase64Encoded: false,
        multiValueHeaders: {},
        multiValueQueryStringParameters: {},
        path: '/hello',
        pathParameters: {},
        queryStringParameters: {},
        requestContext: {
            accountId: '123456789012',
            apiId: '1234',
            authorizer: {},
            httpMethod: 'get',
            identity: {
                accessKey: '',
                accountId: '',
                apiKey: '',
                apiKeyId: '',
                caller: '',
                clientCert: {
                    clientCertPem: '',
                    issuerDN: '',
                    serialNumber: '',
                    subjectDN: '',
                    validity: { notAfter: '', notBefore: '' },
                },
                cognitoAuthenticationProvider: '',
                cognitoAuthenticationType: '',
                cognitoIdentityId: '',
                cognitoIdentityPoolId: '',
                principalOrgId: '',
                sourceIp: '',
                user: '',
                userAgent: '',
                userArn: '',
            },
            path: '/hello',
            protocol: 'HTTP/1.1',
            requestId: 'c6af9ac6-7b61-11e6-9a41-93e8deadbeef',
            requestTimeEpoch: 1428582896000,
            resourceId: '123456',
            resourcePath: '/hello',
            stage: 'dev',
        },
        resource: '',
        stageVariables: {},
    };
});

beforeEach(() => {
    s3Mock.reset();
});

describe('Unit test for app handler', () => {
    it('returns success code and concatenated list for nonempty bucket list', async () => {
        s3Mock.on(ListBucketsCommand).resolves({ Buckets: [{ Name: 'test1' }, { Name: 'test2' }] });
        const result: APIGatewayProxyResult = await listBucketsLambdaHandler(inputEvent);
        expect(result.statusCode).toBe(200);
        expect(result.body).toEqual('test1 | test2');
    });
    it('returns success code and empty list for empty bucket list', async () => {
        s3Mock.on(ListBucketsCommand).resolves({});
        const result: APIGatewayProxyResult = await listBucketsLambdaHandler(inputEvent);
        expect(result.statusCode).toBe(200);
        expect(result.body).toEqual('');
    });
    it('returns failure code and empty list for error getting bucket list', async () => {
        s3Mock.on(ListBucketsCommand).rejects({ message: 'Filed to list buckets' });
        const result: APIGatewayProxyResult = await listBucketsLambdaHandler(inputEvent);
        expect(result.statusCode).toBe(500);
        expect(result.body).toBe('');
    });
});
