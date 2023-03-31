import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import {
  DynamoDBDocumentClient,
  PutCommand,
  DeleteCommand
} from "@aws-sdk/lib-dynamodb";
import { Product } from '../../src/model/Product';

const dynamoDbClient = new DynamoDBClient({});
const ddb = DynamoDBDocumentClient.from(dynamoDbClient);

async function seedData(tableName: string, testData: Product[]){
  const writeCommands = testData.map(item => new PutCommand({ TableName: tableName, Item: item }));
  const writePromises = writeCommands.map(command => ddb.send(command));
  await Promise.all(writePromises);
}

async function unseedData(tableName: string, testData: Product[]){
  const deleteCommands = testData.map(item => new DeleteCommand({ TableName: tableName, Key: { id: item.id }}));
  const deletePromises = deleteCommands.map(command => ddb.send(command));
  await Promise.all(deletePromises);
}

export{
  seedData,
  unseedData
}