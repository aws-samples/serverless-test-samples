// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { describe, it, expect, beforeAll } from '@jest/globals';
import axios from 'axios';
import { MetaProduct } from '../../src/model/Product';
import { DynamoDbStore } from '../../src/store/dynamodb/dynamodb-store';
import { ProductStore } from '../../src/store/product-store';
import { Repeater } from '../helpers/repeater';
import { shortTimestamp } from '../../src/utils.ts/dates';
import { mockVariable } from '../helpers/env';

const repeatInterval = 1000;
const repeatLimit = 10;

jest.setTimeout(repeatInterval * repeatLimit);

const createProducts = (productCount: number) => {
  const products: MetaProduct[] = [];
  for (let i = 0; i < productCount; i++) {
    const index = i + 1;
    const id = `product-${index}`;
    const padCount = String(productCount).length;
    const name = `Product-${String(index).padStart(padCount, '0')}`;
    const amount = 1 + index / 100;
    const price = parseFloat(amount.toFixed(2));
    products.push({ id, name, price, timeCreated: shortTimestamp() });
  }
  return products;
};

describe('API Integration tests: POST Products Async', () => {
  let baseApiUrl: string;

  beforeAll(async () => {
    baseApiUrl = process.env.API_URL as string;

    expect(baseApiUrl).toBeDefined();

    if (baseApiUrl.endsWith('/')) baseApiUrl = baseApiUrl.slice(0, -1);
  });

  describe('POST /products', () => {
    const batchCounts = [3, 5, 10, 15]; // max batch is 10 for SQS
    it.each(batchCounts)('should queue a batch of %s products in SQS and eventually write them to DynamoDB', async (batchCount: number) => {
      const products = createProducts(batchCount);

      const url = `${baseApiUrl}/products`;
      const config = { headers: { Accept: 'application/json' } };
      const response = await axios.post(url, products, config);

      expect(response.status).toBe(201);

      mockVariable('TABLE_NAME', 'Products');
      const store: ProductStore = new DynamoDbStore();

      const maxBatchCount = batchCounts[batchCounts.length - 1];
      const clearDbProducts = createProducts(maxBatchCount).map(async (product) => await store.deleteProduct(product.id));
      await Promise.all(clearDbProducts);

      const lastProduct = products[products.length - 1];
      const getProduct = async () => await store.getProduct(lastProduct.id);
      const repeater = new Repeater({ interval: repeatInterval, limit: repeatLimit });
      const { result: product } = await repeater.repeat(getProduct); // poll for last product in DynamoDB table

      expect(product).toBeDefined();
    });
  });
});
