[![typescript: 4.5.5](https://badgen.net/badge/Built%20With/TypeScript/blue9)](https://badgen.net/badge/Built%20With/TypeScript/blue9)
[![AWS: DynamoDB](https://img.shields.io/badge/AWS-DynamoDB-blueviolet)](https://img.shields.io/badge/AWS-DynamoDB-blueviolet)
[![test: unit](https://img.shields.io/badge/Test-Unit-blue)](https://img.shields.io/badge/Test-Unit-blue)
[![test: integration](https://img.shields.io/badge/Test-Integration-yellow)](https://img.shields.io/badge/Test-Integration-yellow)

# Typescript: Test an AWS Lambda function locally that calls cloud services

## Introduction

The project consists of an [AWS Lambda function](https://aws.amazon.com/lambda/), and an [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) table. Although this project can be deployed, the focus of the code is to demonstrate local testing approaches using TypeScript. This project demonstrates testing an AWS Lambda function handler locally which calls remote cloud services. The Lambda function handler makes a call to a DynamoDB table in the cloud in the integration test. 

---

## Contents

- [Introduction](#introduction)
- [Contents](#contents)
- [About this Pattern](#about-this-pattern)
- [About this Example](#about-this-example)
  - [Key Files in the Project](#key-files-in-the-project)
- [Sample project description](#sample-project-description)
- [Integration Test](#integration-test)
- [Cleanup](#cleanup)

---

## About this Pattern

### System Under Test (SUT)

The SUT in this pattern is an AWS Lambda function that makes calls to other AWS cloud services using an AWS SDK. For this example, we demonstrate a system that generates a new item, written to an Amazon DynamoDB table by the Lambda function.

![System Under Test (SUT)](img/system-under-test.png)

### Goal

This pattern is intended to increase development speed. It enables rapid development and testing of a Lambda function that makes calls to other AWS cloud services using an AWS SDK. This pattern eliminates the need to perform a build and deploy of the Lambda function to the cloud between modifications of test or function code.

### Description

In this pattern you develop a Lambda function that makes calls to Amazon DynamoDB using an AWS SDK. Your tests invoke the handler function method on your local desktop, passing it a synthetic event as a parameter. The handler function executes within your local desktop environment. When the SDK invokes the Amazon DynamoDB table, it uses the [AWS credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html) contained in your local environment, typically as environment variables. The SDK calls resources deployed to the cloud.

In this sample, we have used AWS CDK (Cloud Development Kit) for infrastructure as code but the pattern can be also be used with a variety of systems including SAM, Serverless Framework, CloudFormation and Terraform. This pattern simplifies the process of attaching a debugger to the handler code. You may generate synthetic events using several methods including the ‘sam local generate-event’ command, by copying event template samples in the AWS Lambda console test section, or by printing events to CloudWatch logs.

![Test Pattern](img/pattern_02_lambda_handler_test.png)

### Limitations

The IAM policies contained in your local environment variables may differ from those contained in the execution role attached to the Lambda function in the AWS cloud environment. Therefore this pattern may not accurately test IAM permissions. You may mitigate this risk by using the [IAM Roles Anywhere](https://docs.aws.amazon.com/rolesanywhere/latest/userguide/introduction.html) service to obtain temporary security credentials for the same execution role that the Lambda function uses in the cloud context. This service is open source and you may [view the code on GitHub](https://github.com/aws/rolesanywhere-credential-helper).

[Top](#contents)
---

## About this Example

This example contains an [AWS Lambda](https://aws.amazon.com/lambda/) function and [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) table as core resources.

AWS CDK is used to deploy the AWS Lambda function and Amazon DynamoDB table. The AWS Lambda function generates an item in the JSON format and writes this item to the DynamoDB table using the AWS SDK. The DynamoDB table item is a JSON object with format:

```json
{
    "ID": "string",
    "created": "date",
    "metadata": "json"
}
```

### Key Files in the Project

  - [app.ts](src/app.ts) - Lambda handler code to test
  - [lambda-handler-dynamodb-stack.ts](lib/lambda-handler-dynamodb-stack.ts) - CDK stack for deploying required resources
  - [integ-handler.test.ts](test/integration/integ-handler.test.ts) - Integration tests on a live stack

[Top](#contents)
---

## Integration Test

### Integration Test Description

In order to run integration tests in the cloud we will first need to deploy the full CDK stack which will create a Lambda function and DynamoDB table in your AWS account. The integration test invokes the handler function method on the local machine, passing it a synthetic event as a parameter. The handler function executes within your local environment. When the SDK writes to DynamoDB, it uses the AWS credentials contained in your local environment.

### Run the Integration Tests

[integ-handler.test.ts](test/integration/integ-handler.test.ts) 

Deploy the full stack:

```shell
lambda-handler-dynamodb$ npm install
lambda-handler-dynamodb$ cdk deploy
```
 
The [integration tests](test/integration/integ-handler.test.ts) need to be provided a single environment variable: `DatabaseTable`, which is the name of the DynamoDB table providing persistence.

Set up the environment variable, replacing the `<PLACEHOLDERS>` with your values:

```shell
lambda-handler-dynamodb$ export DatabaseTable=<YOUR_DYNAMODB_TABLE_NAME>
```

Then run the test suite.

```shell
lambda-handler-dynamodb$ npm run test
```

Alternatively, you can set the environment variables and run the test suite all in one command:

```shell
lambda-handler-dynamodb$ DatabaseTable=<YOUR_DYNAMODB_TABLE_NAME> npm run test
```

## Cleanup

In order to delete the sample application that you created, use the AWS cdk command as shown below:

```bash
lambda-handler-dynamodb$ cdk destroy
```

[Top](#contents)