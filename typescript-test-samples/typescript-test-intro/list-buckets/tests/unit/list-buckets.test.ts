// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

/**
 * list-buckets.test.ts
 *
 * Unit tests for the list-buckets Lambda handler function.
 *
 * As the entry point for getting our bucket list, the handler is the seam (or
 * interface) between the service integration calling the lambda - in this case
 * Amazon API Gateway - and the inner business logic of the application.
 *
 * The unit tests here are focused on testing this interface, exercising code
 * paths that validate inbound request payloads and checking for correct
 * behavior when the busines layer returns different results.
 */

/**
 * Import Modules
 *
 * Standard practice to put imports at the top of a module definition.
 */
import { beforeEach, describe, it, expect } from '@jest/globals';
import { mockClient } from 'aws-sdk-client-mock';

import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { S3Client, ListBucketsCommand } from '@aws-sdk/client-s3';

import { listBucketsLambdaHandler } from '../../app';

/**
 * Set up Mocks
 *
 * We are using a mocked Amazon S3 Client for these tests because we have a focus
 * on the interface logic implemented by the handler. We want to be able to reliably
 * validate that when the client calls succeed, we build an appropriate
 * response. We also need to be able to check that errors are returned correctly
 * when the client call fails. Mocks are useful for forcing these success and failure conditions
 */
const s3Mock = mockClient(S3Client);

/**
 * Unit Tests
 *
 * This is the set of unit tests focused on the list-buckets service, testing
 * the lambdaHandler function. We're using `describe` blocks to keep the tests
 * organized both in code and in test output. This also gives us a chance to run
 * subsets of tests easily.
 */
describe('list-buckets', () => {
    describe('lambdaHandler()', () => {
        let inputEvent: APIGatewayProxyEvent;

        /**
         * Shared test setup
         *
         * We're using a `beforeEach` block that runs setup prior to each unit test
         * in this `describe` block. This lets us pull noise out of the test bodies
         * and ensures that setup is consistent.
         *
         * The setup resets our s3Mock client back to its starting point between each
         * unit test. This means we're starting from a clean state with each test.
         *
         * It also gets us a fresh instance of our inputEvent stub, with default values
         * provided. We want to make sure that there is no data or context leaking
         * between tests that could accidentally influence outcomes.
         */
        beforeEach(() => {
            s3Mock.reset();
            inputEvent = getEmptyAPIGatewayProxyEvent();
        });

        /**
         * Unit tests.
         *
         * Now we come to the unit tests themselves. Each test checks a single
         * scenario, with specific responses configured on the S3 client mock.
         *
         * The unit tests use the "Arrange, Act, Assert" pattern, setting up the
         * data (Arrange), executing the handler function (Act), then checking that
         * the result matches the inferface contract we expect (Assert).
         */
        it('returns success code and concatenated list for nonempty bucket list', async () => {
            // Arrange
            s3Mock.on(ListBucketsCommand).resolves({ Buckets: [{ Name: 'test1' }, { Name: 'test2' }] });

            // Act
            const result: APIGatewayProxyResult = await listBucketsLambdaHandler(inputEvent);

            // Assert
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
});

/**
 * Builds an empty API Gateway Proxy Event input object, with default values
 * @returns {APIGatewayProxyEvent}
 */
function getEmptyAPIGatewayProxyEvent(): APIGatewayProxyEvent {
    const result: APIGatewayProxyEvent = {
        body: null,
        headers: {},
        multiValueHeaders: {},
        httpMethod: '',
        isBase64Encoded: false,
        path: '',
        pathParameters: {},
        queryStringParameters: null,
        multiValueQueryStringParameters: null,
        stageVariables: null,
        requestContext: {
            accountId: '',
            apiId: '',
            authorizer: {},
            protocol: '',
            httpMethod: '',
            identity: {
                accessKey: null,
                accountId: null,
                apiKey: null,
                apiKeyId: null,
                caller: null,
                clientCert: null,
                cognitoAuthenticationProvider: null,
                cognitoAuthenticationType: null,
                cognitoIdentityId: null,
                cognitoIdentityPoolId: null,
                principalOrgId: null,
                sourceIp: '',
                user: null,
                userAgent: null,
                userArn: null,
            },
            path: '',
            stage: '',
            requestId: '',
            requestTimeEpoch: 0,
            resourceId: '',
            resourcePath: '',
        },
        resource: '',
    };
    return result;
}
