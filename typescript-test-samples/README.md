[![typescript: 4.9.4](https://img.shields.io/badge/Typescript-4.9.4-green)](https://img.shields.io/badge/Typescript-4.9.4-green)

# TypeScript Test Samples

This project contains code samples for testing serverless applications using TypeScript. 

## Test Patterns

|Project| Description                                                                                                                                                                                                    |
---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
|[TypeScript Test Samples Starter Project](./typescript-test-intro/)| This project contains an introductory example of TypeScript tests written for AWS Lambda and Amazon API Gateway. This is the best place to start!                                                              |
|[Calling Cloud Resources from Local Tests](./lambda-handler-dynamodb/)| This project demonstrates testing an AWS Lambda function handler locally which calls remote cloud services. The Lambda function handler makes a call to a DynamoDB table in the cloud in the integration test. |
|[Testing Serverless architectures with Datadog Synthetic Testing and Monitoring](apigw-lambda-sqs-sns-datadog)| Creates Synthetic Tests and Monitors in Datadog to ensure Serverless services are functioning properly in a real, AWS environment.                                                                             |
|[AWS AppSync, Amazon Cognito, AWS Lambda](appsync-cognito-lambda-aleios)| Examples of TypeScript tests written for AWS AppSync with authentication provided by Amazon Cognito.                                                                                                           |                                                                   |
|[Amazon Kinesis, AWS Lambda, Amazon DynamoDB](kinesis-lambda-dynamodb)| Testing a small data processing system that processes records from an Amazon Kinesis Data Stream and stores the processed records in an Amazon DynamoDB table.                                                 |                                                |
|[Using LaunchDarkly for Testing with AWS Lambda](launchdarkly-lambda-dynamodb)| Use LaunchDarkly feature flags to test new code and features within a serverless application using AWS Lambda.                                                                                                 |                                                                                                |
|[AWS Step Functions Local Testing using Jest](step-functions-local)| Shows how to run Step Functions local tests with mocks using Jest |                                                                                                                                             |


### API Tests

These projects have examples of unit and integration tests for API based applications. 

|Project|Description|
---|---
|[javascript-http-sam](https://github.com/aws-samples/serverless-samples/tree/main/serverless-rest-api/javascript-http-sam) [External]|An implementation of the backend API using AWS API Gateway HTTP endpoint, Node.js and AWS SAM.|
|[Testing Amazon Api Gateway, AWS Lambda, and Amazon DynamoDB](./apigw-lambda-dynamodb/)|This project contains examples of TypeScript unit and integration tests written for AWS Lambda in the context of an Amazon API Gateway API and an Amazon DynamoDB table.|
apigw-lambda-external

## Asynchronous Architectures

In a synchronous system, a calling service makes a request to a receiving service and then blocks, waiting for the receiver to complete the operation and return a result. In contrast, in an **asynchronous system**, a caller makes a request to a receiving system, which typically returns an immediate acknowledgement but then performs the requested operation at a later time. Asynchronous systems are frequently designed using event-driven architectures. These types of systems have several advantages including increased reliability, greater control over load processing, and improved scalability. However, testing these systems can present unique challenges.

[Click this link to learn more about testing asynchronous architectures](./README-ASYNC.md).

|Project|Description|
---|---
|[Async Integration Test Sample](./async-lambda-dynamodb/)|In this pattern, an AWS Lambda function is configured to be an event listener to receive the asynchronous System Under Test's output data.|
|[Testing a Stream-based Architecture](./kinesis-lambda-dynamodb/)|This project contains an example of testing a data processing system that processes records from an Amazon Kinesis Data Stream and stores the processed records in an Amazon DynamoDB table.|
|[Schema and Contract Testing](./schema-and-contract-testing/)|This project contains introductory examples of TypeScript unit tests demonstrating schema and contract testing.|