// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
import { APIGatewayProxyEvent, APIGatewayProxyResult } from "aws-lambda";
import { DynamoDbStore } from "../store/dynamodb/dynamodb-store";
import { ProductStore } from "../store/product-store";
import middy from "@middy/core";
import { captureLambdaHandler} from "@aws-lambda-powertools/tracer";
import { logger, metrics, tracer } from "../powertools/utilities";
import { injectLambdaContext } from "@aws-lambda-powertools/logger";
import { logMetrics, MetricUnits } from "@aws-lambda-powertools/metrics";

const store: ProductStore = new DynamoDbStore();
const lambdaHandler = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {

  logger.appendKeys({
    resource_path: event.requestContext.resourcePath
  });

  const id = event.pathParameters!.id;
  if (id === undefined) {
    logger.warn('Missing \'id\' parameter in path while trying to retrieve a product', {
      details: { eventPathParameters: event.pathParameters }
    });

    return {
      statusCode: 400,
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ message: "Missing 'id' parameter in path" }),
    };
  }
  try {
    const result = await store.getProduct(id);

    if (!result) {
      logger.warn('No product with ID '+ id + ' found in the databases while trying to retrieve a product');

      return {
        statusCode: 404,
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ message: "Product not found" }),
      };
    }

    logger.info('Product retrieved with ID '+ id, { details: { product: result } });
    metrics.addMetric('productRetrieved', MetricUnits.Count, 1);
    metrics.addMetadata('productId', id);

    return {
      statusCode: 200,
      headers: { "content-type": "application/json" },
      body: JSON.stringify(result),
    };
  } catch (error) {
    logger.error('Unexpected error occurred while trying to retrieve a product', error as Error);

    return {
      statusCode: 500,
      headers: { "content-type": "application/json" },
      body: JSON.stringify(error),
    };
  }
};

const handler = middy(lambdaHandler)
    .use(captureLambdaHandler(tracer))
    .use(logMetrics(metrics, { captureColdStartMetric: true }))
    .use(injectLambdaContext(logger, { clearState: true }));

export {
  handler
};