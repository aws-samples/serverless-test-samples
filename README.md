# Serverless Test Samples

![Serverless Test Samples](./_img/main_header.png)

This repository is designed to provide code samples and guidance for writing automated tests for serverless applications and event driven architectures.  

# Getting Started
If you would like to understand our opinionated guidance behind the test samples, please read [Serverless Testing Principles](Serverless-Testing-Principles.md). 

If you are new to serverless testing we recommend you begin with a starter project in your favorite language:
- [Python starter](./python-test-samples/apigw-lambda)
- [Java starter](./java-test-samples/apigw-lambda-list-s3-buckets)
- [TypeScript starter](./typescript-test-samples/typescript-test-intro)
- [.NET starter](./dotnet-test-samples/apigw-lambda-list-s3-buckets)

# Language Directories
The repository is divided into several language directories. If you would like to browse by language you can navigate to the main page of each directory.

- [Python main directory](./python-test-samples/)
- [Java main directory](./java-test-samples/)
- [TypeScript main directory](./typescript-test-samples/)
- [.NET main directory](./dotnet-test-samples/)

# Workload Types
You can also find sample code in this repository for testing a variety of different types of workloads.

## API's
|System Under Test|Language|
---|---
|[API Gateway with Lambda and DynamoDB](./python-test-samples/apigw-lambda-dynamodb)|Python|API Gateway, AWS Lambda and Amazon DynamoDB|
|[API Gateway HTTP with CDK](https://github.com/aws-samples/serverless-samples/tree/main/serverless-rest-api/python-http-cdk) [External] | Python |
|[API Gateway HTTP with SAM](https://github.com/aws-samples/serverless-samples/tree/main/serverless-rest-api/python-http-sam) [External] | Python |
|[API Gateway REST with SAM](https://github.com/aws-samples/serverless-samples/tree/main/serverless-rest-api/python-rest-sam) [External] | Python |
|[Api Gateway, Lambda, DynamoDB](./typescript-test-samples/apigw-lambda-dynamodb)|TypeScript|
|[API Gateway, Lambda Authorizer, Lambda, DynamoDB](https://github.com/aws-samples/serverless-samples/tree/main/serverless-rest-api/javascript-http-sam) [External] | Node.js | 
|[API Gateway, Lambda, DynamoDB](./java-test-samples/apigw-lambda-ddb)|Java|
|[API Gateway, Lambda, DynamoDB](./dotnet-test-samples/apigw-lambda-ddb)|.NET|

## Service Orchestration
|System Under Test|Language|Description|
---|---|---
|[Step Functions](./java-test-samples/step-functions-local) [External]|Java|This project shows a technique for testing an AWS Step Functions workflow in a local desktop environment.


## Event-Driven Architectures
Event-driven architectures (EDA) are an architecture style that uses events and asynchronous communication to loosely couple an application’s components. To learn more about several strategies for testing EDA's visit [this guide at Serverlessland.com](https://serverlessland.com/event-driven-architecture/testing-introduction).  
|System Under Test|Language|Description|
---|---|---
|[S3, Lambda](./python-test-samples/async-lambda-dynamodb)|Python|This is a great starter project for learning how to test async EDA.|
|[Schemas and Contracts](./typescript-test-samples/schema-and-contract-testing)|TypeScript|Event driven architectures decouple producers and consumers at the infrastructure layer, but these resources may still be coupled at the application layer by the event contract. Learn how to test for breaking changes in the contract.|
