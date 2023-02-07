// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

/**
 * get-products.test.ts
 *
 * Unit tests for the get-products Lambda handler function.
 *
 * As the entry point for getting our product list, the handler is the seam (or
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
import { beforeEach, describe, it, expect, jest } from '@jest/globals';

import { APIGatewayProxyEvent, Context } from 'aws-lambda';
import apiGWProxyEventStub from '../events/unit-test-event.json';

import { DynamoDbStore } from "../src/store/dynamodb/dynamodb-store";
import { Product } from '../src/model/Product';
import { handler } from '../src/api/get-products';

jest.mock('../src/store/dynamodb/dynamodb-store');

const mockedStore = jest.mocked(DynamoDbStore);

describe( 'get-products', () => {

  describe( 'lambdaHandler()', () => {

    let inputEvent: APIGatewayProxyEvent;
    let inputContext: Context;

    beforeEach(() => {
      inputEvent = apiGWProxyEventStub;
      inputContext = {
        callbackWaitsForEmptyEventLoop: false,
        functionName: '',
        functionVersion: '',
        invokedFunctionArn: '',
        memoryLimitInMB: '',
        awsRequestId: '',
        logGroupName: '',
        logStreamName: '',
        getRemainingTimeInMillis: () => 1000,
        done: function (error?: Error | undefined, result?: any): void {
          throw new Error('Function not implemented.');
        },
        fail: function (error: string | Error): void {
          throw new Error('Function not implemented.');
        },
        succeed: function (messageOrObject: any): void {
          throw new Error('Function not implemented.');
        }
      };
    });

    it('exists', () => {
      expect(handler).toBeTruthy();
    });

    it('returns 200 when finding products', async () => {
      mockedStore.prototype.getProducts.mockImplementationOnce(() => Promise.resolve([]));
      
      const result = await handler(inputEvent, inputContext);
      expect(mockedStore).toHaveBeenCalled();
      expect(mockedStore.prototype.getProducts).toHaveBeenCalled();
      expect(result.statusCode).toBe(200);
    });

    it('returns 500 when getting an error from the store', async () => {
      mockedStore.prototype.getProducts.mockImplementationOnce(() => {
        throw new Error('Test Error');
      });
      
      const result = await handler(inputEvent, inputContext);
      expect(mockedStore).toHaveBeenCalled();
      expect(mockedStore.prototype.getProducts).toHaveBeenCalled();
      expect(result.statusCode).toBe(500);
    });

  });

} );