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
|Architecture Components|Language|
---|---
|[API Gateway with Lambda and DynamoDB](./python-test-samples/apigw-lambda-dynamodb)|Python|API Gateway, AWS Lambda and Amazon DynamoDB|
|[API Gateway HTTP with CDK](https://github.com/aws-samples/serverless-samples/tree/main/serverless-rest-api/python-http-cdk) [External] | Python |
|[API Gateway HTTP with SAM](https://github.com/aws-samples/serverless-samples/tree/main/serverless-rest-api/python-http-sam) [External] | Python |
|[API Gateway REST with SAM](https://github.com/aws-samples/serverless-samples/tree/main/serverless-rest-api/python-rest-sam) [External] | Python |
|[Api Gateway, Lambda, DynamoDB](./typescript-test-samples/apigw-lambda-dynamodb)|TypeScript|
|[API Gateway, Lambda Authorizer, Lambda, DynamoDB](https://github.com/aws-samples/serverless-samples/tree/main/serverless-rest-api/javascript-http-sam) [External] | Node.js | 
|[API Gateway, Lambda, DynamoDB](./java-test-samples/apigw-lambda-ddb)|Java|
|[API Gateway, Lambda, DynamoDB](./dotnet-test-samples/apigw-lambda-ddb)|.NET|


### Event-Driven Architecture / Asynchronous System Test Samples
- [Testing async in Python](https://github.com/aws-samples/serverless-test-samples/tree/main/python-test-samples/async-architectures)
