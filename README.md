
[![test: unit](https://img.shields.io/badge/Test-Unit-blue)](https://img.shields.io/badge/Test-Unit-blue)
[![test: integration](https://img.shields.io/badge/Test-Integration-yellow)](https://img.shields.io/badge/Test-Integration-yellow)
[![.NET: 6](https://badgen.net/badge/Built%20With/.NET/blue9)](https://badgen.net/badge/Built%20With/.NET/blue9)
[![Java: 11](https://badgen.net/badge/Built%20With/Java/blue9)](https://badgen.net/badge/Built%20With/Java/blue9)
[![python: 3.9](https://badgen.net/badge/Built%20With/Python/blue9)](https://badgen.net/badge/Built%20With/Python/blue9)
[![typescript: 4.5.5](https://badgen.net/badge/Built%20With/TypeScript/blue9)](https://badgen.net/badge/Built%20With/TypeScript/blue9)


![Serverless Test Samples](./_img/main_header.png)
# Serverless Test Samples

AWS guidance and examples for testing serverless and event driven applications.


# Getting Started
We recommend reviewing the companion website for this repository: [Serverlessland - Testing Serverless Applications](https://serverlessland.com/testing). 

If you'd like to jump right into code, you can begin with a starter project in your favorite language:

- [Python starter](./python-test-samples/apigw-lambda)
- [Java starter](./java-test-samples/apigw-lambda-list-s3-buckets)
- [TypeScript starter](./typescript-test-samples/typescript-test-intro)
- [.NET starter](./dotnet-test-samples/apigw-lambda-list-s3-buckets)

# Language Directories
The repository is divided into several language directories. If you would like to browse by language, you can navigate to the main page of each language directory:

- [Python main directory](./python-test-samples/)
- [Java main directory](./java-test-samples/)
- [TypeScript main directory](./typescript-test-samples/)
- [.NET main directory](./dotnet-test-samples/)

# Workload Types
This repository contains sample code for testing a variety of different types of workloads, including API's, Event-Driven Architectures, Service Orchestration, Data Processing, and AWS Partner Patterns.

## API's
| System Under Test|Language|
|---|---|
| [API Gateway with Lambda and DynamoDB](./python-test-samples/apigw-lambda-dynamodb)|Python|API Gateway, AWS Lambda and Amazon DynamoDB|
| [API Gateway HTTP with CDK](https://github.com/aws-samples/serverless-samples/tree/main/serverless-rest-api/python-http-cdk) [External]| Python |
| [API Gateway HTTP with SAM](https://github.com/aws-samples/serverless-samples/tree/main/serverless-rest-api/python-http-sam) [External]| Python |
| [API Gateway REST with SAM](https://github.com/aws-samples/serverless-samples/tree/main/serverless-rest-api/python-rest-sam) [External]| Python |
| [Api Gateway, Lambda, DynamoDB](./typescript-test-samples/apigw-lambda-dynamodb)|TypeScript|
| [API Gateway, Lambda Authorizer, Lambda, DynamoDB](https://github.com/aws-samples/serverless-samples/tree/main/serverless-rest-api/javascript-http-sam) [External] | Node.js |
| [API Gateway, Lambda, S3](./dotnet-test-samples/apigw-lambda-list-s3-buckets)|.NET|
| [API Gateway, Lambda, DynamoDB](./dotnet-test-samples/apigw-lambda-ddb)|.NET|
| [SQS, Lambda, DynamoDB](./dotnet-test-samples/sqs-lambda)|.NET|
| [API Gateway, Lambda, DynamoDB](./java-test-samples/apigw-lambda-ddb)|Java|
| [AppSync, DynamoDB](./java-test-samples/java-appsync-sam)|Java|

## Event-Driven Architectures
Event-driven architectures (EDA) are an architecture style that uses events and asynchronous communication to loosely couple an application’s components. To learn more about several strategies for testing EDA's visit [this guide at Serverlessland.com](https://serverlessland.com/event-driven-architecture/testing-introduction).  
|System Under Test|Language|Description|
---|---|---
|[S3, Lambda](./python-test-samples/async-lambda-dynamodb)|Python|This is a great starter project for learning how to test async EDA.|
|[Schemas and Contracts](./typescript-test-samples/schema-and-contract-testing)|TypeScript|Event driven architectures decouple producers and consumers at the infrastructure layer, but these resources may still be coupled at the application layer by the event contract. Learn how to test for breaking changes in the contract.|
|[S3, Lambda, DynamoDB](./dotnet-test-samples/async-lambda-dynamodb)|.NET|This example shows how to test async system by using DynamoDB during to store incoming asynchronous events during testing|
|[S3, Lambda, SQS](./dotnet-test-samples/async-lambda-sqs)|.NET|An example to how to test asynchronous workflow by long polling the queue that resulting messages are sent to.|

## Architectural patterns
|Pattern|Services used|Language|Description|
|---|---|---|---|
| [Hexagonal architecture](./dotnet-test-samples/hexagonal-architecture/) |API Gateway, Lambda, DynamoDB|.NET|Hexagonal architecture is an architectural pattern used for encapsulating domain logic and decoupling it from other implementation details, such as infrastructure or client requests.|

## Service Orchestration
|System Under Test|Language|Description|
|---|---|---|
| [Step Functions](./java-test-samples/step-functions-local) [External] |Java|This project shows a technique for testing an AWS Step Functions workflow in a local desktop environment.|
| [Step Functions](./java-test-samples/step-functions-local-helloworld) |Python|This project demostrates how to test a "Hello World" AWS Step Functions workflow locally using Docker and PyTest.| 
| [Step Functions](./java-test-samples/step-functions-local-lambda) |Python|This project shows a technique for testing an AWS Step Functions state machines that integrate with Lambda functions locally.|
| [Step Functions](./java-test-samples/step-functions-local-mock) |Python|This project shows a technique for testing an AWS Step Functions workflows locally using service mocks.|

## Data Processing
| System Under Test|Language|Description|
|---|---|---|
|[Kinesis Data Stream, Lambda](./typescript-test-samples/kinesis-lambda-dynamodb)|TypeScript|This project shows a technique for testing a streaming data processing system.|
|[Kinesis Data Stream, Lambda, DynamoDB](./dotnet-test-samples/kinesis-lambda-dynamodb)|.NET|This pattern creates an AWS Lambda function that consumes messages from an Amazon Kinesis Data Streams and dumps them to Amazon DynamoDB using SAM and .NET 6.|

## AWS Partner Patterns
| Partner |System Under Test|Language|Description|
|---|---|---|---|
| Datadog |[API Gateway, Lambda, SQS, SNS](./typescript-test-samples/apigw-lambda-sqs-sns-datadog)|TypeScript|This example is about creating Synthetic Tests and Monitors with Datadog.|
| LaunchDarkly |[Lambda, DynamoDB](./typescript-test-samples/launchdarkly-lambda-dynamodb) |TypeScript|Get started using LaunchDarkly feature flags to test new code and features with AWS Lambda.|

## Test Containers
[Testcontainers](https://testcontainers.com/) is an open source framework for providing throwaway, lightweight instances of databases, message brokers, web browsers, or just about anything that can run in a Docker container. These tests demonstrate how you can utilize this as part of your testing frameworks to startup, initialize and tear down emulated resources.

Emulation is not a replacement for testing against actual cloud resources, and integration tests will always run against deployed versions of your applications. However, the emulation of certain services like DynamoDB can provide fast feedback loops on your local machine.

|System Under Test|Language|Description|
|---|---|---|
|[API Gateway, Lambda, DynamoDB](./dotnet-test-samples/test-containers)|.NET|This example demonstrates how you can simplify local testing and emulation using the TestContainers project.|

# How do I contribute?

See our [Contributing](./CONTRIBUTING.md) guide for more detail providing additions, enhancements, and edits.

