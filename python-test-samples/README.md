[![python: 3.9](https://img.shields.io/badge/Python-3.9-green)](https://img.shields.io/badge/Python-3.9-green)

# Python Test Samples

This portion of the repository contains code samples for testing serverless applications using Python. 

## Test Basic Patterns
|Project|Description|
---|---
|[Python Starter Project](./apigw-lambda)|This project contains introductory examples of Python tests written for AWS Lambda. This is the best place to start!|
|[Integrated Application Test Kit](./integrated-application-test-kit)|This sample demonstrates how you can use the [AWS Integrated Application Test Kit (IATK)](https://awslabs.github.io/aws-iatk/) to develop integration tests for your serverless and event-driven applications.|
|[Lambda local testing with Mocks](./lambda-mock)|This project contains unit tests for Lambda using mocks.|
|[Lambda Layers with Mocks](./apigw-lambda-layer)|This project contains unit tests for Lambda layers using mocks.|
|[API Gateway with Lambda and DynamoDB](./apigw-lambda-dynamodb)|This project contains unit and integration tests for a pattern using API Gateway, AWS Lambda and Amazon DynamoDB.|
|[API Gateway with local Lambda and local DynamoDB](./apigw-lambda-dynamodb-crud-local)|This project contains unit test for local execution CRUD paterns using API Gateway, AWS Lambda and Amazon DynamoDB.|
|[Schema and Contract Testing](./schema-and-contract-testing)|This project contains sample schema and contract tests for an event driven architecture.|
|[Kinesis with Lambda and DynamoDB](./kinesis-lambda-dynamodb)|This project contains a example of testing an application with an Amazon Kinesis Data Stream.|
|[SQS with Lambda](./apigw-sqs-lambda-sqs)|This project demonstrates testing SQS as a source and destination in an integration test|
|[Step Functions Local](./step-functions-local)| An example of testing Step Functions workflow locally using pytest and Testcontainers | 

## Test API's
These projects have excellent in-depth examples of unit and integration tests for API based applications. 
|Project|Description|
|---|---|
|[API Gateway HTTP with CDK](https://github.com/aws-samples/serverless-samples/tree/main/serverless-rest-api/python-http-cdk) [External] | An implementation of a backend HTTP API using Python and AWS CDK
|[API Gateway HTTP with SAM](https://github.com/aws-samples/serverless-samples/tree/main/serverless-rest-api/python-http-sam) [External] | An implementation of a backend HTTP API using Python and AWS SAM
|[API Gateway REST with SAM](https://github.com/aws-samples/serverless-samples/tree/main/serverless-rest-api/python-rest-sam) [External] | An implementation of a backend REST API using Python and AWS SAM

## Test Asynchronous Architectures
In a synchronous system, a calling service makes a request to a receiving service and then blocks, waiting for the receiver to complete the operation and return a result. In contrast, in an **asynchronous system**, a caller makes a request to a receiving system, which typically returns an immediate acknowledgement but then performs the requested operation at a later time. Asynchronous systems are frequently designed using event-driven architectures. These types of systems have several advantages including increased reliability, greater control over load processing, and improved scalability. However, testing these systems can present unique challenges.

[Click this link to learn more about testing asynchronous architectures](./README-ASYNC.md).

|Project|Description|
|---|---|
|[Asynchronous Lambda and DynamoDB](./async-lambda-dynamodb)|This project contains tests for an Asynchronous pattern using AWS Lambda and Amazon DynamoDB.|
