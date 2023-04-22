// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
import { AnyProduct } from "../../model/Product";
import { ProductStore } from "../product-store";
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import {
  DeleteCommand,
  DynamoDBDocumentClient,
  GetCommand,
  GetCommandOutput,
  PutCommand,
  ScanCommand,
} from "@aws-sdk/lib-dynamodb";
import { captureAWSv3Client } from "aws-xray-sdk-core";
import { tracer } from '../../powertools/utilities';

export class DynamoDbStore implements ProductStore {
  private readonly tableName: string;
  private static ddbClient: DynamoDBClient = captureAWSv3Client(new DynamoDBClient({}));
  //private static ddbClient: DynamoDBClient = new DynamoDBClient({});
  private static ddbDocClient: DynamoDBDocumentClient =
    DynamoDBDocumentClient.from(DynamoDbStore.ddbClient);

  constructor() {
    if (!process.env.TABLE_NAME) {
      throw new Error('TABLE_NAME environment variable is not defined');
    }
    this.tableName = process.env.TABLE_NAME;
  }

  @tracer.captureMethod()
  public async getProduct(id: string): Promise<AnyProduct | undefined> {
    const params: GetCommand = new GetCommand({
      TableName: this.tableName,
      Key: {
        id: id,
      },
    });
    const result:GetCommandOutput = await DynamoDbStore.ddbDocClient.send(params);
    return result.Item as AnyProduct;
  };

  @tracer.captureMethod()
  public async putProduct(product: AnyProduct): Promise<void> {
    const params: PutCommand = new PutCommand({
      TableName: this.tableName,
      Item: product,
    });
    await DynamoDbStore.ddbDocClient.send(params);
  };

  @tracer.captureMethod()
  public async deleteProduct(id: string): Promise<void> {
    const params: DeleteCommand = new DeleteCommand({
      TableName: this.tableName,
      Key: {
        id: id,
      },
    });
    await DynamoDbStore.ddbDocClient.send(params);
  };

  @tracer.captureMethod()
  public async getProducts (): Promise<AnyProduct[] | undefined> {
    const params:ScanCommand = new ScanCommand( {
        TableName: this.tableName,
        Limit: 20
    });
    const result = await DynamoDbStore.ddbDocClient.send(params);
    return result.Items as AnyProduct[];
  };
}
