# Test Asynchronous Architectures

This section contains code samples for testing asynchronous architectures using Typescript. 

## Generic Asynchronous System Patterns
Asynchronous systems typically receive messages or events and immediately store them for future processing. Later, a secondary processing service may perform operations on the stored data. Processed data may then be sent as output to additional services or placed into another storage location. Below is a diagram illustrating a generic asynchronous pattern.

![Generic Asynchronous System](./img/generic.png)

## Create Event Listeners as Test Resources
When testing asynchronous systems, you will establish event listeners that are only used for testing purposes. These event listeners will be configured to receive the output of your system under test (SUT). These test resources will be deployed to pre-production environments. If your production environment can tolerate the introduction of test data, you may decide to deploy these resources to production as well.

## Execute Tests and Poll for Results
Your tests will establish a connection to the event listeners, and then perform polling actions against them with some reasonable timeout. The tests will send input data to the SUT. The SUT will process the data and send output to the event listener. The polling action will eventually retrieve the output data and examine it for the expected result. 

![Generic Asynchronous System Test](./img/generic-async-test.png)

### Asynchronous Test Samples
|Project|Description|
---|---
|[Lambda with DynamoDB](./async-lambda-dynamodb/)|You may use a variety of resource types to create the event listener for your asynchronous system under test. We recommend starting with AWS Lambda and Amazon DynamoDB. DynamoDB creates a persistent storage resource that can enable long running tests or an aggregate a set of results.|
