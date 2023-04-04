// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
import { CfnOutput, RemovalPolicy, Stack, StackProps } from "aws-cdk-lib";
import { Construct } from "constructs";
import {
  aws_apigateway,
  aws_lambda_nodejs,
  aws_dynamodb,
  aws_logs,
  aws_lambda,
} from "aws-cdk-lib";

export class ServerlessTypescriptDemoStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const productsTable = new aws_dynamodb.Table(this, "Products", {
      tableName: "Products",
      partitionKey: {
        name: "id",
        type: aws_dynamodb.AttributeType.STRING,
      },
      billingMode: aws_dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: RemovalPolicy.DESTROY
    });

    const envVariables = {
      AWS_ACCOUNT_ID: Stack.of(this).account,
      POWERTOOLS_SERVICE_NAME: 'serverless-typescript-demo',
      POWERTOOLS_LOGGER_LOG_LEVEL: 'WARN',
      POWERTOOLS_LOGGER_SAMPLE_RATE: '0.01',
      POWERTOOLS_LOGGER_LOG_EVENT: 'true',
      POWERTOOLS_METRICS_NAMESPACE: 'AwsSamples',
  };

    const esBuildSettings = {
      minify: true
    }

    const functionSettings = {
      handler: "handler",
      runtime: aws_lambda.Runtime.NODEJS_16_X,
      memorySize: 256,
      environment: {
        TABLE_NAME: productsTable.tableName,
        ...envVariables
      },
      logRetention: aws_logs.RetentionDays.ONE_WEEK,
      tracing: aws_lambda.Tracing.ACTIVE,
      bundling: esBuildSettings
    }

    const getProductsFunction = new aws_lambda_nodejs.NodejsFunction(
      this,
      "GetProductsFunction",
      {
        awsSdkConnectionReuse: true,
        entry: "./src/api/get-products.ts",
        ...functionSettings
      }
    );

    const getProductFunction = new aws_lambda_nodejs.NodejsFunction(
      this,
      "GetProductFunction",
      {
        awsSdkConnectionReuse: true,
        entry: "./src/api/get-product.ts",
        ...functionSettings
      }
    );

    const putProductFunction = new aws_lambda_nodejs.NodejsFunction(
      this,
      "PutProductFunction",
      {
        awsSdkConnectionReuse: true,
        entry: "./src/api/put-product.ts",
        ...functionSettings
      }
    );

    const deleteProductFunction = new aws_lambda_nodejs.NodejsFunction(
      this,
      "DeleteProductsFunction",
      {
        awsSdkConnectionReuse: true,
        entry: "./src/api/delete-product.ts",
        ...functionSettings
      }
    );

    productsTable.grantReadData(getProductsFunction);
    productsTable.grantReadData(getProductFunction);
    productsTable.grantWriteData(deleteProductFunction);
    productsTable.grantWriteData(putProductFunction);

    const api = new aws_apigateway.RestApi(this, "ProductsApi", {
      restApiName: "ProductsApi",
      deployOptions: {
        tracingEnabled: true,
        dataTraceEnabled: true,
        loggingLevel: aws_apigateway.MethodLoggingLevel.INFO,
        metricsEnabled: true,
      }
    });

    const products = api.root.addResource("products");
    products.addMethod(
      "GET",
      new aws_apigateway.LambdaIntegration(getProductsFunction)
    );

    const product = products.addResource("{id}");
    product.addMethod(
      "GET",
      new aws_apigateway.LambdaIntegration(getProductFunction)
    );
    product.addMethod(
      "PUT",
      new aws_apigateway.LambdaIntegration(putProductFunction)
    );
    product.addMethod(
      "DELETE",
      new aws_apigateway.LambdaIntegration(deleteProductFunction)
    );

    new CfnOutput(this, "ApiURL", {
      value: `${api.url}products`,
    });
  }
}
