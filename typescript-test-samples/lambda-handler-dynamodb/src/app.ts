import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import {
    PutCommand,
    DynamoDBDocumentClient
} from "@aws-sdk/lib-dynamodb";
const moment = require('moment');
const dynamodb = new DynamoDBClient({ region: 'us-east-1' });
const ddb = DynamoDBDocumentClient.from(dynamodb);

export const lambdaHandler = async function main( event: any ) {
  let params = {
    TableName : process.env.DatabaseTable,
    Item: {
      ID: event.Records[0].eventID,
      created: moment().format('YYYYMMDD-hhmmss'),
      metadata:JSON.stringify(event),
    }
  }
  try {
    await ddb.send(new PutCommand(params));
  }
  catch (err) {
    console.log(err);
    return err;
  }
  return {
    statusCode: 200,
    body: 'OK!',
  };
}