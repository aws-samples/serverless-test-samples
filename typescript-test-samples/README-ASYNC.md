# Test Asynchronous Architectures

This section contains code samples for testing asynchronous architectures using Typescript. 

## Generic Asynchronous System Patterns
Asynchronous systems typically receive messages or events and immediately store them for future processing. Later, a secondary processing service may perform operations on the stored data. Processed data may then be sent as output to additional services or placed into another storage location. Below is a diagram illustrating a generic asynchronous pattern.

![Generic Asynchronous System](./img/generic-async-system.png)

## Create Event Listeners as Test Resources
When testing asynchronous systems, you will establish event listeners that are only used for testing purposes. These event listeners will be configured to receive the output of your system under test (SUT). These test resources will be deployed to pre-production environments. If your production environment can tolerate the introduction of test data, you may decide to deploy these resources to production as well.

## Execute Tests and Poll for Results
Your tests will establish a connection to the event listeners, and then perform polling actions against them with some reasonable timeout. The tests will send input data to the SUT. The SUT will process the data and send output to the event listener. The polling action will eventually retrieve the output data and examine it for the expected result. 

![Generic Asynchronous System Test](./img/generic-async-test.png)

### Asynchronous Test Samples
| Project                                                        |Description|
----------------------------------------------------------------|---
|[Async Integration Test Sample](./async-lambda-dynamodb/)|In this pattern, an AWS Lambda function is configured to be an event listener to receive the asynchronous System Under Test's output data.|
|[Testing a Stream-based Architecture](./kinesis-lambda-dynamodb/)|This project contains an example of testing a data processing system that processes records from an Amazon Kinesis Data Stream and stores the processed records in an Amazon DynamoDB table.|
|[Schema and Contract Testing](./schema-and-contract-testing/)|This project contains introductory examples of TypeScript unit tests demonstrating schema and contract testing.|