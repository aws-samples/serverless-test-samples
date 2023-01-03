[![python: 3.9](https://img.shields.io/badge/Python-3.9-green)](https://img.shields.io/badge/Python-3.9-green)

# Python Test Samples

This project contains code samples for testing serverless applications using Python. 

## Test Basic Patterns
* [Python Starter project](./apigw-lambda): This project contains introductory examples of Python tests written for AWS Lambda. This is the best place to start!
* [Lambda Layers with Mocks](./apigw-lambda-layer) : This project contains unit tests for Lambda layers using mocks.
* [API Gateway with Lambda and DynamoDB](./apigw-lambda-dynamodb) : This project contains unit and integration tests for a pattern using API Gateway, AWS Lambda and Amazon DynamoDB.

## Test Asynchronous Architectures
* In a synchronous system, a calling service makes a request to a receiving service and then blocks, waiting for the receiver to complete the operation and return a result. In contrast, in an **asynchronous system**, a caller makes a request to a receiving system, which typically returns an immediate acknowledgement but then performs the requested operation at a later time. Asynchronous systems are frequently designed using event-driven architectures. These types of systems have several advantages including increased reliability, greater control over load processing, and improved scalability. However, testing these systems can present unique challenges.
* [Learn more about testing asynchronous architectures](./async-architectures)


## Test API's
These projects have excellent examples of unit and integration tests for API based applications. 
* [API Gateway HTTP with CDK](https://github.com/aws-samples/serverless-samples/tree/main/serverless-rest-api/python-http-cdk) : [External] an implementation of a backend HTTP API using Python and AWS CDK
* [API Gateway HTTP with SAM](https://github.com/aws-samples/serverless-samples/tree/main/serverless-rest-api/python-http-sam) : [External] an implementation of a backend HTTP API using Python and AWS SAM
* [API Gateway REST with SAM](https://github.com/aws-samples/serverless-samples/tree/main/serverless-rest-api/python-rest-sam) : [External] an implementation of a backend REST API using Python and AWS SAM
