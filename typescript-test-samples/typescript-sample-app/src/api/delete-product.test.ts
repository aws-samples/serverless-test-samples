// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

/**
 * delete-product.test.ts
 *
 * Unit tests for the delete-product Lambda handler function.
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

import { APIGatewayProxyEvent } from 'aws-lambda';
import apiGWProxyEventStub from '../../events/unit-test-event.json';

import { Product } from "../model/Product";
import { DynamoDbStore } from "../store/dynamodb/dynamodb-store";
import { handler } from '../api/delete-product';
import { inputContext } from '../../test/stubs/api-gateway-input-context';

jest.mock('../store/dynamodb/dynamodb-store');

const mockedStore = jest.mocked(DynamoDbStore);

describe( 'delete-products', () => {

  describe( 'lambdaHandler()', () => {

    let inputEvent: APIGatewayProxyEvent;

    beforeEach(() => {
      inputEvent = apiGWProxyEventStub;
      mockedStore.mockReset();
      mockedStore.prototype.deleteProduct.mockReset();
    });

    it('exists', () => {
      expect(handler).toBeTruthy();
    });

    it('returns HTTP status code 200 when no errors from store', async () => {
      if(inputEvent.pathParameters === null)
        fail('inputEvent.pathParameters is null');
      inputEvent.pathParameters.id = '1';

      mockedStore.prototype.deleteProduct.mockImplementationOnce(() => {
        return Promise.resolve();
      });

      const result = await handler(inputEvent, inputContext);
      expect(mockedStore.prototype.deleteProduct).toHaveBeenCalledTimes(1);
      expect(mockedStore.prototype.deleteProduct).toHaveBeenCalledWith('1');
      expect(result.statusCode).toBe(200);
    });

    it('returns HTTP status code 400 when input product id is undefined', async () => {
      if(inputEvent.pathParameters === null)
        fail('inputEvent.pathParameters is null');
      inputEvent.pathParameters.id = undefined;

      const result = await handler(inputEvent, inputContext);
      expect(mockedStore.prototype.deleteProduct).toHaveBeenCalledTimes(0);
      expect(result.statusCode).toBe(400);

      const resultBody = JSON.parse(result.body);
      expect(resultBody.message).toBeDefined();
      expect(resultBody.message).toBe("Missing 'id' parameter in path");
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

      mockedStore.prototype.deleteProduct.mockImplementationOnce(() => {
        throw new Error('Test Error');
      })

      const result = await handler(inputEvent, inputContext);
      expect(mockedStore.prototype.deleteProduct).toHaveBeenCalledTimes(1);
      expect(mockedStore.prototype.deleteProduct).toHaveBeenCalledWith('1');
      expect(result.statusCode).toBe(500);
    });

  });

} );