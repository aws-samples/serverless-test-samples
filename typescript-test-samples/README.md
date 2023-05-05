[![typescript: 4.9.4](https://img.shields.io/badge/Typescript-4.9.4-green)](https://img.shields.io/badge/Typescript-4.9.4-green)

# TypeScript Test Samples

This project contains code samples for testing serverless applications using TypeScript. 

## Test Patterns

|Project|Description|
---|---
|[TypeScript Test Samples Starter Project](./typescript-test-intro/)|This project contains an introductory example of TypeScript tests written for AWS Lambda and Amazon API Gateway. This is the best place to start!|

### API Tests

These projects have examples of unit and integration tests for API based applications. 

|Project|Description|
---|---
|[javascript-http-sam](https://github.com/aws-samples/serverless-samples/tree/main/serverless-rest-api/javascript-http-sam) [External]|An implementation of the backend API using AWS API Gateway HTTP endpoint, Node.js and AWS SAM.|
|[Testing Amazon Api Gateway, AWS Lambda, and Amazon DynamoDB](./apigw-lambda-dynamodb/)|This project contains examples of TypeScript unit and integration tests written for AWS Lambda in the context of an Amazon API Gateway API and an Amazon DynamoDB table.|

## Event Driven Architectures

|Project|Description|
---|---
|[Async Integration Test Sample](./async-architectures/async-lambda-dynamodb/)|In this pattern, an AWS Lambda function is configured to be an event listener to receive the asynchronous System Under Test's output data.|
|[Testing a Stream-based Architecture](./kinesis-lambda-dynamodb/)|This project contains an example of testing a data processing system that processes records from an Amazon Kinesis Data Stream and stores the processed records in an Amazon DynamoDB table.|
|[Schema and Contract Testing](./schema-and-contract-testing/)|This project contains introductory examples of TypeScript unit tests demonstrating schema and contract testing.|