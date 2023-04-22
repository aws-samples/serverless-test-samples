import { SQSEvent, SQSRecord } from 'aws-lambda';
import { DynamoDbStore } from '../store/dynamodb/dynamodb-store';
import { ProductStore } from '../store/product-store';
import { MetaProduct } from '../model/Product';
import { shortTimestamp } from '../utils.ts/dates';
import { formatJson } from '../utils.ts/strings';

const store: ProductStore = new DynamoDbStore();

export const handler = async (event: SQSEvent): Promise<void> => {
  try {
    const putProductPromises = event.Records.map(async (record) => {
      const product: MetaProduct = JSON.parse(record.body);
      product.timeStored = shortTimestamp();
      await store.putProduct(product);
      console.log(`put product: ${formatJson(product)}`);
    });
    await Promise.all(putProductPromises);
  } catch (error) {
    console.log('putting products failed: ', error)
  }
  
};
