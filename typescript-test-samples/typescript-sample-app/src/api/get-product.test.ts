// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

/**
 * get-product.test.ts
 *
 * Unit tests for the get-product Lambda handler function.
 *
 * As the entry point for getting a single product, the handler is the seam (or
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

import { DynamoDbStore } from "../store/dynamodb/dynamodb-store";
import { Product } from '../model/Product';
import {inputContext} from '../../test/stubs/api-gateway-input-context';

import { handler } from '../api/get-product';

jest.mock('../store/dynamodb/dynamodb-store');

const mockedStore = jest.mocked(DynamoDbStore);

describe( 'get-products', () => {

  describe( 'lambdaHandler()', () => {

    let inputEvent: APIGatewayProxyEvent;

    beforeEach(() => {
      inputEvent = apiGWProxyEventStub;
      mockedStore.mockReset();
      mockedStore.prototype.getProduct.mockReset();
    });

    it('exists', () => {
      expect(handler).toBeTruthy();
    });

    it('returns HTTP status code 200 when no errors from store', async () => {
      if(inputEvent.pathParameters === null)
        fail('inputEvent.pathParameters is null');
      inputEvent.pathParameters.id = '1';

      const product = {id: '1', name: 'one', price: 1.00} as Product;
      mockedStore.prototype.getProduct.mockImplementationOnce(id => Promise.resolve(product));
      
      const result = await handler(inputEvent, inputContext);
      expect(mockedStore.prototype.getProduct).toHaveBeenCalledWith('1');
      expect(result.statusCode).toBe(200);
    });

    it('returns HTTP status code 400 when input product id is undefined', async () => {
      if(inputEvent.pathParameters === null)
        fail('inputEvent.pathParameters is null');
      inputEvent.pathParameters.id = undefined;

      mockedStore.prototype.getProduct.mockImplementationOnce(() => {
        throw new Error('Test Error from 400');
      });

      const result = await handler(inputEvent, inputContext);
      expect(inputEvent.pathParameters.id).toBeUndefined();
      expect(mockedStore.prototype.getProduct).toHaveBeenCalledTimes(0);
      expect(result.statusCode).toBe(400);
    });

    it('returns HTTP status code 404 when product store does not have a match', async () => {
      if(inputEvent.pathParameters === null)
        fail('inputEvent.pathParameters is null');
      inputEvent.pathParameters.id = '1';
      mockedStore.prototype.getProduct.mockImplementationOnce(id => Promise.resolve(undefined));

      const result = await handler(inputEvent, inputContext);
      expect(mockedStore.prototype.getProduct).toHaveBeenCalledWith('1');
      expect(result.statusCode).toBe(404);
    });

    it('returns a matching Product when product store has products', async () => {
      if(inputEvent.pathParameters === null)
        fail('inputEvent.pathParameters is null');
      inputEvent.pathParameters.id = '1';

      const product = {id: '1', name: 'one', price: 1.00} as Product;
      mockedStore.prototype.getProduct.mockImplementationOnce(id => Promise.resolve(product));
      
      const result = await handler(inputEvent, inputContext);
      expect(mockedStore.prototype.getProduct).toHaveBeenCalledWith('1');
      
      const parsedBody = JSON.parse(result.body);
      expect(parsedBody).toEqual(product);
    });

    it('returns HTTP status code 500 when getting an error from the store', async () => {
      mockedStore.prototype.getProduct.mockImplementationOnce(() => {
        throw new Error('Test Error');
      });
      
      const result = await handler(inputEvent, inputContext);
      expect(mockedStore.prototype.getProduct).toHaveBeenCalled();
      expect(result.statusCode).toBe(500);
    });

  });

} );