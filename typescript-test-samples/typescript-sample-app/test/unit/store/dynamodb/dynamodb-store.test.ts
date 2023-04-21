/**
 * dynamodb-store.test.ts
 *
 * Unit tests for the dynamodb-store module
 */

/**
 * Import Modules
 *
 * Standard practice to put imports at the top of a module definition.
 */
import { beforeEach, describe, it, expect, jest } from '@jest/globals';
import { 
  DynamoDBDocumentClient, 
  DeleteCommand,
  GetCommand,
  PutCommand,
  ScanCommand,
} from "@aws-sdk/lib-dynamodb";

import { mockClient } from 'aws-sdk-client-mock';

import { Product } from "../../../../src/model/Product";
import { DynamoDbStore } from '../../../../src/store/dynamodb/dynamodb-store';
import exp from 'constants';
import { table } from 'console';

/**
 * Set up Mocks
 * Mock the DynamoDB Client from the AWS SDK so that we can control
 */
const mockDynamoDBClient = mockClient(DynamoDBDocumentClient);

/**
 * Tests begin here with a describe block for each externally-accessible
 * function on the module.
 * 
 * In this case, we're testing a class, so we'll be exercising the 
 * public methods on the class.
 */
describe( 'dynamodb-store', () => {

  // The dynamo store needs this environment variable set to work properly
  expect(process.env.TABLE_NAME).toBeDefined();

  beforeEach(() => {
    mockDynamoDBClient.reset();
  });

  describe( 'getProduct()', () => {

    it( 'queries the data store with the given product id', async () => {
      let store = new DynamoDbStore();

      mockDynamoDBClient
        .on(GetCommand, { TableName: process.env.TABLE_NAME, Key: { id: '1' } })
        .resolves({ Item: { id: '1', name: 'product1', price: 123.45 }, })
        .on(GetCommand, { TableName: process.env.TABLE_NAME, Key: { id: '2' } })
        .resolves({ Item: { id: '2', name: 'product2', price: 123.45 }, });

        const p = await store.getProduct('1');

        expect(p).toBeDefined();
        expect(p?.id).toBe('1');
        expect(p?.name).toBe('product1');
        expect(p?.price).toBe(123.45);
    });
  });

  describe( 'getProducts()', () => { 
    it( 'queries the data store for an array of products', async () => {
      let store = new DynamoDbStore();

      mockDynamoDBClient
        .on(ScanCommand)
        .resolves({
          Items: [
            { id: '1', name: 'product1', price: 123.45 },
            { id: '2', name: 'product2', price: 123.45 },
            { id: '3', name: 'product3', price: 123.45 },
          ]
        });

        const p = await store.getProducts() as Product[];

        expect(p).toBeDefined();
        expect(p?.length).toBe(3);

        const firstProduct = p[0];
        expect(firstProduct.id).toBe('1');
        expect(firstProduct.name).toBe('product1');
        expect(firstProduct.price).toBe(123.45);
    });
  });

  describe( 'putProduct()', () => { 
    it( 'writes the given product to the data store', async () => {
      let store = new DynamoDbStore();

      mockDynamoDBClient
        .on(PutCommand)
        .resolves({ });

      const p: Product = {
        id: '1',
        name: 'product1',
        price: 123.45
      };

      await store.putProduct(p);

      const calls = mockDynamoDBClient.calls();
      const lastCall = calls[0];
      expect(lastCall).toBeDefined();
      expect(lastCall.lastArg.input.Item).toStrictEqual(p);
    });
  });

  describe( 'deleteProduct()', () => { 
    it( 'issues a delete command to the store for the given id', async () => {
      let store = new DynamoDbStore();

      mockDynamoDBClient
        .on(DeleteCommand,{
          TableName: process.env.TABLE_NAME,
          Key: { id: '1' }
        })
        .resolves({ });

      await store.deleteProduct('1');

      const calls = mockDynamoDBClient.calls();
      const lastCall = calls[0];
      expect(lastCall).toBeDefined();
      expect(lastCall.lastArg.input.Key).toStrictEqual({id: '1'});
    });
  });

});