# Java Test Samples

This portion of the repository contains test samples for Java based serverless projects.
|Project|Description|
|---|---|
|[Java Starter Project](apigw-lambda-list-s3-buckets)|An introductory example of Java AWS Lambda and Amazon API Gateway integration test. This is the best place to start!|
|[API Gateway to Lambda to DynamoDB](apigw-lambda-ddb)|An example of simple serverless microservice with Amazon API Gateway, Java AWS Lambda and Amazon DynamoDB with tests.|
|[Step Functions Local Testing](step-functions-local)|An example of testing Step Functions workflow locally using JUnit, Spock test framework, and Testcontainers.|
|[Springboot with DynamoDB Application](fargate-dynamodb-sync)| Synchronous sample SpringBoot application written in Java which performs customer CRUD operations. AWS serverless services like Amazon API Gateway, ALB, ECR, Fargate, DynamoDB & SQS being used to host and test the application flow.|
|[GraphQL using AppSync](java-appsync-sam)| An implementation of the backend GraphQL API using Java with AWS Java SDK 2.x and AWS SAM. |
|[Step Functions Local](./step-functions-local)| This project shows a technique for testing an AWS Step Functions workflow locally | 

## Test Asynchronous Architectures
In a synchronous system, a calling service makes a request to a receiving service and then blocks, waiting for the receiver to complete the operation and return a result. In contrast, in an **asynchronous system**, a caller makes a request to a receiving system, which typically returns an immediate acknowledgement but then performs the requested operation at a later time. Asynchronous systems are frequently designed using event-driven architectures. These types of systems have several advantages including increased reliability, greater control over load processing, and improved scalability. However, testing these systems can present unique challenges.

[Click this link to learn more about testing asynchronous architectures](./README-ASYNC.md).

|Project|Description|
---|---
|[Lambda with DynamoDB](./async-lambda-dynamodb/)|You may use a variety of resource types to create the event listener for your asynchronous system under test. We recommend starting with AWS Lambda and Amazon DynamoDB. DynamoDB creates a persistent storage resource that can enable long running tests or an aggregate a set of results.|
|[Schema & Contract Testing](./schema-and-contract-testing)|This project contains examples on how to do schema and contract testing for your event driven applications.|
