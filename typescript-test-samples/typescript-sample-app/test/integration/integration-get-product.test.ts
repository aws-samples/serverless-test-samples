// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

/**
 * integration-get-product.test.ts
 *
 * Integration tests for the get-product API Endpoint
 *
 * The integration tests here are focused on testing the API Gateway
 * endpoint serving individual products to validate that IAM
 * policies are working correctly and the system adheres to the API
 * contact that clients are expecting.
 * 
 * Note that we initially seed the database with records. This means
 * the test runner needs access to that database, including
 * AWS credentials and network path. In this case we use the AWS SDK
 * to pull credentials from the local environment.
 * 
 * We do *not* use the 'create product' endpoint to seed the database
 * because we have not validated that it works as expected.
 */

/**
 * Import Modules
 *
 * Standard practice to put imports at the top of a module definition.
 */
import { describe, it, expect } from '@jest/globals';
import axios, { AxiosResponse } from 'axios';
import { seedData, unseedData } from '../helpers/dynamodb-test-helpers';

import { Product } from '../../src/model/Product';

/**
 * Validate environment
 */
if(!process.env.API_URL)
  throw new Error('API_URL environment variable not set.');

if(!process.env.TABLE_NAME)
  throw new Error('TABLE_NAME environment variable not set.');

describe('API Integration tests: GET Product', () => {
  /**
   * Shared test setup
   *
   * In this case, we're using a beforeAll block to pull configuration from
   * our environment. These tests need a base URL to make HTTP requests against 
   * and DynamoDB table name to populate the database.
   * 
   * We don't want to commit this URL into our source code beacuse it may change
   * as we develop code, and between different environments like QA and Production.
   */

  /**
   * Seed data... one thing to notice here: we have a handful of test suites
   * that all use the same DynamoDB table. This means that we could have 
   * collisions of record ids. For example, a product delete test may remove
   * one of the records we expect to be there, if we use colliding ids
   * In this case, we're namespacing the ids to this test suite to avoid such 
   * collisions.
   */
  const testData: Product[] = [
    {id: 'get-product-1', name: 'get-product-product1', price: 111.22},
    {id: 'get-product-2', name: 'get-product-product2', price: 222.33},
  ]

  let baseApiUrl :string;

  beforeAll(async () => {
    baseApiUrl = process.env.API_URL as string;
    if(!baseApiUrl.endsWith('/')) baseApiUrl += '/';

    await seedData(process.env.TABLE_NAME as string, testData);
  });

  afterAll(async () => {
    await unseedData(process.env.TABLE_NAME as string, testData);
  });

  describe( 'GET /product/{id}', () => {
    it('returns an existing product record for a valid id', async () => {
      const testRecord = testData[0];
      const url = `${baseApiUrl}/products/${testRecord.id}`;

      const response = await axios.get(url, {'headers': {'Accept': 'application/json'}});
      expect(response.status).toBe(200);
      expect(response.data).toStrictEqual(testRecord);
    });

    it('returns a 404 for an invalid id', async () => {
      const url = `${baseApiUrl}/products/doesnotexist`;

      let response: AxiosResponse<any, any>;
      try {
        response = await axios.get(url, {'headers': {'Accept': 'application/json'}});
      } catch (err){
        if(axios.isAxiosError(err)){
          expect(err!.response!.status).toBe(404);
        } else {
          expect(axios.isAxiosError(err)).toBeTruthy();
        }
      }
    });
  });
});