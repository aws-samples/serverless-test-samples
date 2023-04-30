[![typescript: 4.5.5](https://badgen.net/badge/Built%20With/TypeScript/blue9)](https://badgen.net/badge/Built%20With/TypeScript/blue9)
[![AWS: DynamoDB](https://img.shields.io/badge/AWS-DynamoDB-blueviolet)](https://img.shields.io/badge/AWS-DynamoDB-blueviolet)
[![test: unit](https://img.shields.io/badge/Test-Unit-blue)](https://img.shields.io/badge/Test-Unit-blue)
[![test: integration](https://img.shields.io/badge/Test-Integration-yellow)](https://img.shields.io/badge/Test-Integration-yellow)

# Typescript: Test locally an AWS Lambda function handler that calls remote cloud services.

## Introduction

The project consists of an [AWS Lambda function](https://aws.amazon.com/lambda/), an [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) table. Although this project can be deployed, the focus of the code is to demonstrate local testing approaches using typescript. This project demonstrates testing locally an AWS Lambda function handler that calls remote cloud services. The Lambda function handler is being called locally which makes a call to DynamoDB table in cloud in the integration test. 

---

## Contents

- [Introduction](#introduction)
- [Contents](#contents)
- [System Under Test (SUT)](#system-under-test-sut)
- [Goal](#goal)
- [Description](#description)
- [Key Files in the Project](#key-files-in-the-project)
- [Prerequisites](#prerequisites)
- [Make commands for test and deployment](#make-commands-for-test-and-deployment)
- [Running the project](#running-the-project)

---

### System Under Test (SUT)

The SUT in this pattern is a Lambda function that makes calls to other AWS cloud services using an AWS SDK. For this example, we demonstrate a system that generates a document, written to Amazon S3, based on contents from a key-value lookup in DynamoDB.

![System Under Test (SUT)](img/system-under-test.png)

An API Gatway path [1] triggers an AWS Lambda function [2] that retrieves a data from a DynamoDB [3] table and writes data to a object on Amazon S3 [4]. The API path contains a Document Type and a Customer ID. The Lambda function retrieves both the Document Type data and Customer ID data and combines them, writing the data to S3 and returning the object key [1]. The DynamoDB table name and the S3 bucket name are provided to the Lambda function via environment variables. 

The DynamoDB table schema is comprised of a Partition Key (PK) for looking up a given item, and a “data” field containing string contents. Document Type Items are prefixed with D#, and Customer items have a PK prefixed with C#.

[Top](#contents)

---

### Goal

This pattern is intended to enable rapid development and testing of a Lambda function that makes calls to other AWS services. Testing occurs on a local desktop environment and does not affect cloud resources. This pattern speeds development by eliminating the need to perform a build and deploy of the Lambda function to the cloud between modifications of test or function code. This pattern eliminates the need to access cloud resources to conduct tests. Mock tests are also useful for testing failure conditions within your code, especially when mocking third party services beyond your control.

[Top](#contents)

---

### Description

In this pattern, you develop a Lambda function that makes calls to other AWS cloud services using an AWS SDK. The test first sets up mocked versions of the AWS services accessed by the Lambda function. Your tests then invoke the handler function on your local desktop, passing a synthetic event as a parameter. During the test the calls to external cloud services are handled instead by the mocked objects, returning the pre-configured results set up by the test code. 

This pattern can be used with a variety of infrastructure as code systems including SAM, Serverless Framework, CDK, CloudFormation and Terraform. This pattern uses a simple test framework, with the test harness directly calling the Lambda function handlers. No cloud resources or full ** stack emulation are required.

![Test Pattern](img/pattern_04_lambda_mock_test.png)

[Top](#contents)
---

### Key Files in the Project

  - [app.ts](src/app.ts) - Lambda handler code to test
  - [template.yaml](template.yaml) - SAM script for deployment
  - [test-handler.test.ts](src/tests/unit/test-handler.test.ts) - Unit test using mocks
  - [integ-handler.test.ts](src/tests/integration/integ-handler.test.ts) - Integration tests on a live stack

[Top](#contents)
---

## Run the Unit Tests
[test-handler.test.ts](src/tests/unit/test-handler.test.ts) 

In the [unit test](src/tests/unit/test-handler.test.ts#L44), all references and calls to the DynamoDB service are mocked using aws-sdk-client-mock client.
To run the unit tests
``` shell
local-lambda-dynamodb$ cd src
src $ npm install
src $ npm run test:unit
```

[Top](#contents)

---

## Run the Integration Tests
[integ-handler.test.ts](src/tests/integration/integ-handler.test.ts) 

For integration tests, deploy the full stack before testing:
```shell
local-lambda-dynamodb$ sam build
local-lambda-dynamodb$ sam deploy --guided
```
 
The [integration tests](src/tests/integration/integ-handler.test.ts) need to be provided 2 environment variables. 

1. The `DYNAMODB_TABLE_NAME` is the name of the DynamoDB table providing persistence. 
    * The integration tests [seed data into the DynamoDB table](src/tests/integration/integ-handler.test.ts#L24-28).
    * The [integration test tear-down](src/tests/integration/integ-handler.test.ts#L30-49) removes the seed data, as well as data generated during the test.
2. 

Set up the environment variables, replacing the `<PLACEHOLDERS>` with your values:
```shell
src $ export DYNAMODB_TABLE_NAME=<YOUR_DYNAMODB_TABLE_NAME>
src $ export 
```

Then run the test suite.
```shell
apigw-lambda-dynamodb$ cd src
src $ npm install
src $ npm run test:integration
```

Alternatively, you can set the environment variables and run the test suite all in one command:
```shell
apigw-lambda-dynamodb$ cd src
src $ npm install
src $ DYNAMODB_TABLE_NAME=<YOUR_DYNAMODB_TABLE_NAME> API_URL=<YOUR_APIGATEWAY_BASE_URL> npm run test:integration
```

[Top](#contents)