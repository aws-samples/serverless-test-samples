// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import middy from '@middy/core';
import { MetricUnits, logMetrics } from '@aws-lambda-powertools/metrics';
import { SQSEvent } from 'aws-lambda';
import { captureLambdaHandler } from '@aws-lambda-powertools/tracer';
import { injectLambdaContext } from '@aws-lambda-powertools/logger';
import { DynamoDbStore } from '../store/dynamodb/dynamodb-store';
import { MetaProduct } from '../model/Product';
import { ProductStore } from '../store/product-store';
import { logger, tracer, metrics } from '../powertools/utilities';
import { shortTimestamp } from '../utils/dates';


const store: ProductStore = new DynamoDbStore();

const lambdaHandler = async (event: SQSEvent): Promise<void> => {
  logger.appendKeys({
    product_count: event.Records.length,
  });

  try {
    const putProductPromises = event.Records.map(async (record) => {
      const product: MetaProduct = JSON.parse(record.body);
      product.timeStored = shortTimestamp();
      logger.info('putting product', { product });
      await store.putProduct(product);
    });
    await Promise.all(putProductPromises);
    metrics.addMetric('productsPut', MetricUnits.Count, event.Records.length);
  } catch (error) {
    logger.error('putting products failed', { error });
  }
};

export const handler = middy(lambdaHandler)
  .use(captureLambdaHandler(tracer))
  .use(logMetrics(metrics, { captureColdStartMetric: true }))
  .use(injectLambdaContext(logger, { clearState: true }));
