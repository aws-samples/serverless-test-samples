[![.NET: 6.0](https://img.shields.io/badge/.NET-6.0-Green)](https://img.shields.io/badge/.NET-6.0-Green)

# .NET Test Samples

This portion of the repository contains code samples for testing serverless applications using .NET

## Test Basic Patterns
|Project|Description|
|---|---|
|[.NET Starter Project](./apigw-lambda-list-s3-buckets)|This project contains introductory examples of .NET tests written for AWS Lambda. This is the best place to start!|
|[API Gateway with AWS Lambda and DynamoDB](./apigw-lambda-ddb)|This project contains unit and integration tests for a pattern using API Gateway, AWS Lambda and Amazon DynamoDB.|
|[Hexagonal Architecture](./hexagonal-architecture)|An example of hexagonal architecture implemented using AWS Lambda with tests.|
|[Kinesis Data Streams](./kinesis-lambda-dynamodb/)|This project contains unit and integration tests for a pattern using Kinesis Data Streams, AWS Lambda and Amazon DynamoDB.|
|[SQS with AWS Lambda and DynamoDb](./sqs-lambda)|This project contains unit and integration tests for AWS Lambda that is invoked by Amazon Simple Queue Service (SQS)|


## Test Asynchronous Architectures
* In a synchronous system, a calling service makes a request to a receiving service and then blocks, waiting for the receiver to complete the operation and return a result. In contrast, in an **asynchronous system**, a caller makes a request to a receiving system, which typically returns an immediate acknowledgement but then performs the requested operation at a later time. Asynchronous systems are frequently designed using event-driven architectures. These types of systems have several advantages including increased reliability, greater control over load processing, and improved scalability. However, testing these systems can present unique challenges.

|Project|Description|
|---|---|
|[Schema & Contract Testing](./schema-and-contract-testing)|This project contains examples on how to do schema and contract testing for your event driven applications.|
|[Async Testing Introduction](./apigw-lambda-ddb)|This project contains an introduction to asynchronous testing using Lambda, S3 & DynamoDB.|

