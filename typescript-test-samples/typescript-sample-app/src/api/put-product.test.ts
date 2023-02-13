// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

/**
 * put-product.test.ts
 *
 * Unit tests for the put-product Lambda handler function.
 *
 * As the entry point for saving a product, the handler is the seam (or
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
import apiGWProxyEventStub from '../../events/unit-test-event.json';

import { Product } from "../model/Product";
import { DynamoDbStore } from "../store/dynamodb/dynamodb-store";
import { handler } from '../api/put-product';

jest.mock('../store/dynamodb/dynamodb-store');

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

      mockedStore.mockReset();
      mockedStore.prototype.putProduct.mockReset();
    });

    it('exists', () => {
      expect(handler).toBeTruthy();
    });

    it('returns HTTP status code 201 when no errors from store', async () => {
      if(inputEvent.pathParameters === null)
        fail('inputEvent.pathParameters is null');
      inputEvent.pathParameters.id = '1';

      const inputBody : Product = {
        id: '1',
        name: 'one',
        price: 100.01
      };
      inputEvent.body = JSON.stringify(inputBody);

      mockedStore.prototype.putProduct.mockImplementationOnce(() => {
        return Promise.resolve();
      });

      const result = await handler(inputEvent, inputContext);
      expect(mockedStore.prototype.putProduct).toHaveBeenCalledTimes(1);
      expect(mockedStore.prototype.putProduct).toHaveBeenCalledWith(inputBody);
      expect(result.statusCode).toBe(201);
    });

    it('returns HTTP status code 400 when input product id is undefined', async () => {
      if(inputEvent.pathParameters === null)
        fail('inputEvent.pathParameters is null');
      inputEvent.pathParameters.id = undefined;

      const inputBody : Product = {
        id: '1',
        name: 'one',
        price: 100.01
      };
      inputEvent.body = JSON.stringify(inputBody);

      const result = await handler(inputEvent, inputContext);
      expect(mockedStore.prototype.putProduct).toHaveBeenCalledTimes(0);
      expect(result.statusCode).toBe(400);

      const resultBody = JSON.parse(result.body);
      expect(resultBody.message).toBeDefined();
      expect(resultBody.message).toBe("Missing 'id' parameter in path");
    });

    it('returns HTTP status code 400 when input product body is falsy', async () => {
      if(inputEvent.pathParameters === null)
        fail('inputEvent.pathParameters is null');
      inputEvent.pathParameters.id = '1';
      inputEvent.body = null;

      const result = await handler(inputEvent, inputContext);
      expect(mockedStore.prototype.putProduct).toHaveBeenCalledTimes(0);
      expect(result.statusCode).toBe(400);

      const resultBody = JSON.parse(result.body);
      expect(resultBody.message).toBeDefined();
      expect(resultBody.message).toBe("Empty request body");
    });

    it('returns HTTP status code 400 when input product body not parseable', async () => {
      if(inputEvent.pathParameters === null)
        fail('inputEvent.pathParameters is null');
      inputEvent.pathParameters.id = '1';

      const inputBody = 'one';
      inputEvent.body = JSON.stringify(inputBody);

      const result = await handler(inputEvent, inputContext);
      expect(mockedStore.prototype.putProduct).toHaveBeenCalledTimes(0);
      expect(result.statusCode).toBe(400);

      const resultBody = JSON.parse(result.body);
      expect(resultBody.message).toBeDefined();
      expect(resultBody.message).toBe("Failed to parse product from request body");
    });

    it('returns HTTP status code 400 when input product body id does not match path id', async () => {
      if(inputEvent.pathParameters === null)
        fail('inputEvent.pathParameters is null');
      inputEvent.pathParameters.id = '2';

      const inputBody : Product = {
        id: '1',
        name: 'one',
        price: 100.01
      };
      inputEvent.body = JSON.stringify(inputBody);

      const result = await handler(inputEvent, inputContext);
      expect(mockedStore.prototype.putProduct).toHaveBeenCalledTimes(0);
      expect(result.statusCode).toBe(400);

      expect(inputEvent.pathParameters.id).not.toBe(inputBody.id);

      const resultBody = JSON.parse(result.body);
      expect(resultBody.message).toBeDefined();
      expect(resultBody.message).toBe("Product ID in path does not match product ID in body");
    });

    it('returns HTTP status code 500 when getting an error from the store', async () => {
      if(inputEvent.pathParameters === null)
        fail('inputEvent.pathParameters is null');
      inputEvent.pathParameters.id = '1';

      const inputBody : Product = {
        id: '1',
        name: 'one',
        price: 100.01
      };
      inputEvent.body = JSON.stringify(inputBody);

      mockedStore.prototype.putProduct.mockImplementationOnce(() => {
        throw new Error('Test Error');
      })

      const result = await handler(inputEvent, inputContext);
      expect(mockedStore.prototype.putProduct).toHaveBeenCalledTimes(1);
      expect(result.statusCode).toBe(500);
    });

  });

} );