import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { MetaProduct } from '../model/Product';
import { SQSClient, SendMessageBatchCommand, SendMessageBatchCommandInput, SendMessageBatchRequestEntry } from '@aws-sdk/client-sqs';
import { v4 as uuid } from 'uuid';
import { shortTimestamp } from '../utils.ts/dates';
import { formatJson } from '../utils.ts/strings';

const sqsClient = new SQSClient({});

const sendBatchedProducts = async (batchedProducts: MetaProduct[]): Promise<null | unknown> => {
  const entries: SendMessageBatchRequestEntry[] = batchedProducts.map((product) => {
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
      console.log('Success, message sent.', formatJson(data));
    }
    return null; // no error
  } catch (err) {
    console.log('Error', err);
    return err;
  }
};

export const handler = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
  const products = JSON.parse(event.body ?? '[]') as MetaProduct[];

  while (products.length) {
    const batchedProducts = products.splice(0, 10); // max batch size is 10 for SQS

    const error = await sendBatchedProducts(batchedProducts);
    if (error) {
      return {
        statusCode: 500,
        body: formatJson('Some error occurred '),
      };
    }
  }

  return {
    statusCode: 201,
    body: formatJson({ message: `${products.length} products queued` }),
  };
};
