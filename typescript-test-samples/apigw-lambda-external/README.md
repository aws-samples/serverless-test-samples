[![typescript: 5.3.2](https://badgen.net/badge/Built%20With/TypeScript/blue9)](https://badgen.net/badge/Built%20With/TypeScript/blue9)
[![test: unit](https://img.shields.io/badge/Test-Unit-blue)](https://img.shields.io/badge/Test-Unit-blue)
[![test: integration](https://img.shields.io/badge/Test-Integration-yellow)](https://img.shields.io/badge/Test-Integration-yellow)

# Typescript: Amazon Api Gateway, AWS Lambda, External API dependency

## Introduction

This project contains introductory examples of TypeScript tests written for AWS Lambda. This example test pattern showcases a typical REST api communicating with an external service via a Lambda with a pattern for siloing the testing of deployed resources to not be reliant on the status of external systems as part of the pipeline or validation.

Just as units tests apply the spotlight on the code and not testing external behaviour or state. API mocking is showcased here to enable focus on integration testing on deployed AWS resources and will allow consistent validation of connected AWS resources without tightly coupling the business solution to the availability of external systems.

When mocking external APIs to provide validation that the deployed system functions as expected, this gives up the direct communication to an external system. There are many factors that could put the deployed system in a state of error outside of this integration process running such as authentication changes and API schema updates. These changes could take effect at anytime or in any environment utilised from the external system, and it is due to this that deployed systems should contain suitable observability to provide a full suite of validation.

The project uses the [AWS Serverless Application Model](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) (SAM) CLI for configuration, testing and deployment.

---

## Contents

- [Introduction](#introduction)
- [Contents](#contents)
- [About this Pattern](#about-this-pattern)
- [About this Example](#about-this-example)
  - [Key Files in the Project](#key-files-in-the-project)
- [Run the Unit Test](#run-the-unit-tests)
- [Run the Integration Test](#run-the-integration-tests)

---

## About this Pattern

### System Under Test (SUT)

The SUT in this pattern is a synchronous API composed of Amazon API Gateway, AWS Lambda and a simple external API.

![System Under Test (SUT)](img/system-under-test.png)

### Goal

The goal of this pattern is to test the SUT in an environment as similar to production as possible by running tests against resources deployed to the cloud but not communicating with an external API.

### Description

The SUT will be deployed to the AWS cloud. The test code will create an HTTP client that will send requests to the deployed API Gateway endpoint. The endpoint will invoke the backing services, test resource configuration, IAM permissions, authorizers, and internal business logic of the SUT. The SUT will not have any dependency on the external API, resulting in the service not being negatively impacted by the constraints or idiosyncrasies of external systems, ensuring that this system remains robust whilst under test.

![System Under Test Description (SUT)](img/system-under-test-description.png)

## [Top](#contents)

## About this Example

This sample project allows a user to call an API endpoint with a city location to retrieve the weather and multi day forecast using an external api [https://goweather.herokuapp.com/weather](https://goweather.herokuapp.com/weather). In this example the AWS API Gateway and AWS Lambda are acting as a proxy and providing no specific business logic over the response from the weather API. Although this example isn't adding additional logic, production systems commonly implement business logic at this layer.

This project consists of an [API Gateway](https://aws.amazon.com/api-gateway/), a single [AWS Lambda](https://aws.amazon.com/lambda) function, and an [API Gateway](https://aws.amazon.com/api-gateway/) mock of the external dependency.

### Key Files in the Project

- [app.ts](src/app.ts) - Lambda handler code to test
- [template.yaml](template.yaml) - SAM Template for deployment
- [test-handler.test.ts](src/tests/unit/test-handler.test.ts) - Unit test using mocks
- [integration-handler.test.ts](src/tests/integration/integration-handler.test.ts) - Integration tests on a live stack

## [Top](#contents)

## Run the Unit Tests

[test-handler.test.ts](src/tests/unit/test-handler.test.ts)

In the [unit test](src/tests/unit/test-handler.test.ts#L15), all calls to the external dependency are mocked. At unit level it is best practice to mock external dependencies, to isolate and focus on the code being tested and not on the behavior or state of external dependencies.

To run the unit tests

```shell
apigw-lambda-external$ cd src
src $ npm install
src $ npm run test:unit
```

[Top](#contents)

---

## Run the Integration Tests

[integration-handler.test.ts](src/tests/integration/integration-handler.test.ts)

As this sample contains reference to an external API, to perform the integration tests without the dependency a volatile resource [API Gateway](https://aws.amazon.com/api-gateway/) is required to behave as the external API. To achieve this an additional parameter `IsVolatile` is required during the `sam deploy` step. This will instruct the cloudformation to deploy the mock api and configure the Lambda to utilise this API Gateway.

To provide the value for `IsVolatile`, it is possible to provide an override with the initial command by including `--parameter-overrides IsVolatile=true`. This will override the guided process and update the default value to `true`. Alternatively, this can be provided as part of the guided flow.

```shell
Stack Name [sam-app]:
AWS Region [eu-west-1]:
Parameter IsVolatile [true]:
#Shows you resources changes to be deployed and require a 'Y' to initiate deploy
Confirm changes before deploy [y/N]:
```

[More info](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-deploy.html#ref-sam-cli-deploy-options-parameter-overrides) on `--parameter-overrides` from AWS

For integration tests, deploy the full stack before testing:

```shell
apigw-lambda-external$ sam build
apigw-lambda-external$ sam deploy --guided --parameter-overrides IsVolatile=true
```

The [integration tests](src/tests/integration/integration-handler.test.ts) need to be provided 1 environment variable.

1. The `API_URL` is the base URL of the API Gateway including deployment stage, which would end with `/Prod` in this case. This is available in the `outputs` as `WeatherFunctionApi`

Set up the environment variables, replacing the `<PLACEHOLDERS>` with your values:

```shell
src $ export API_URL=<YOUR_APIGATEWAY_BASE_URL>
```

Then run the test suite.

```shell
apigw-lambda-external$ cd src
src $ npm install
src $ npm run test:integration
```

Alternatively, you can set the environment variables and run the test suite all in one command:

```shell
apigw-lambda-external$ cd src
src $ npm install
src $ API_URL=<YOUR_APIGATEWAY_BASE_URL> npm run test:integration
```

[Top](#contents)
