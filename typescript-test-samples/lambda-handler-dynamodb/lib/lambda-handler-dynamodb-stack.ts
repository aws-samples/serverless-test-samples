import * as cdk from 'aws-cdk-lib';
import { Duration, RemovalPolicy } from 'aws-cdk-lib';
import { AttributeType, Table } from 'aws-cdk-lib/aws-dynamodb';
import { Runtime } from 'aws-cdk-lib/aws-lambda';
import { NodejsFunction } from 'aws-cdk-lib/aws-lambda-nodejs';
import { Construct } from 'constructs';
import path = require('path');

export class LambdaHandlerDynamodbStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // DynamoDB Table
    const dynamoTable = new Table(this, 'DynamoTable', {
      partitionKey: {name:'ID', type: AttributeType.STRING},
      removalPolicy: RemovalPolicy.DESTROY
    });

    // Lambda function
    const lambdaPutDynamoDB = new NodejsFunction(this, 'lambdaPutDynamoDBHandler', {
      runtime: Runtime.NODEJS_16_X,
      memorySize: 1024,
      timeout: Duration.seconds(3),
      entry: path.join(__dirname, '../src/app.ts'),
      handler: 'main',
      environment: {
        DatabaseTable: dynamoTable.tableName
      }
    });

    // Write permissions for Lambda
    dynamoTable.grantWriteData(lambdaPutDynamoDB);

    // Outputs
    new cdk.CfnOutput(this, 'DynamoDbTableName', { value: dynamoTable.tableName });
    new cdk.CfnOutput(this, 'LambdaFunctionArn', { value: lambdaPutDynamoDB.functionArn });
    
  }
}
