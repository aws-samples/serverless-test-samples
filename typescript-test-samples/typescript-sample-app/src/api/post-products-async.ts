import middy from '@middy/core';
import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { MetaProduct } from '../model/Product';
import { MetricUnits, logMetrics } from '@aws-lambda-powertools/metrics';
import { SQSClient, SendMessageBatchCommand, SendMessageBatchCommandInput, SendMessageBatchRequestEntry } from '@aws-sdk/client-sqs';
import { captureLambdaHandler } from '@aws-lambda-powertools/tracer';
import { injectLambdaContext } from '@aws-lambda-powertools/logger';
import { logger, tracer, metrics } from "../powertools/utilities"
import { shortTimestamp } from '../utils.ts/dates';
import { v4 as uuid } from 'uuid';


const sqsClient = new SQSClient({});

const sendProducts = async (products: MetaProduct[]): Promise<null | unknown> => {
  const entries: SendMessageBatchRequestEntry[] = products.map((product) => {
    product.timeQueued = shortTimestamp();
    return {
      Id: uuid(),
      MessageBody: JSON.stringify(product),
      DelaySeconds: 3,
    };
  });

  const sendMessageParams: SendMessageBatchCommandInput = {
    QueueUrl: process.env.QUEUE_URL,
    Entries: entries,
  };

  try {
    const data = await sqsClient.send(new SendMessageBatchCommand(sendMessageParams));
    if (data) {
      logger.info('Success, message sent.', { data });
      metrics.addMetric('productsSent', MetricUnits.Count, products.length);
    }
    return null; // no error
  } catch (err) {
    logger.error('Error', { error: err });
    return err;
  }
};

const lambdaHandler = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
  logger.appendKeys({
    resource_path: event.requestContext.resourcePath
  });

  let products = JSON.parse(event.body ?? '[]') as MetaProduct[];
  let errorPromises = [];

  while (products.length) {
    const batchedProducts = products.splice(0, 10); // max batch size is 10 for SQS
    const error = await sendProducts(batchedProducts);
    errorPromises.push(error);
  }

  const errors = await Promise.all(errorPromises);
  return errors.some((error) => error)
    ? {
        statusCode: 500,
        body: JSON.stringify('Some error occurred '),
      }
    : {
        statusCode: 201,
        body: JSON.stringify({ message: `${products.length} products queued` }),
      };
};

export const handler = middy(lambdaHandler)
    .use(captureLambdaHandler(tracer))
    .use(logMetrics(metrics, { captureColdStartMetric: true }))
    .use(injectLambdaContext(logger, { clearState: true }));
