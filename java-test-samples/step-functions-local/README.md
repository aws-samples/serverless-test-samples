# Step Functions Local Testing 
This project shows a technique for testing an [AWS Step Functions](https://aws.amazon.com/step-functions/) workflow in a local desktop environment. 
The sample contained here is located in [this external repository](https://github.com/aws-samples/aws-stepfunctions-examples/tree/main/sam/demo-local-testing-using-java)
and was originally described in [this blog post](https://aws.amazon.com/blogs/compute/mocking-service-integrations-with-aws-step-functions-local/).

## Goal
Step Functions workflows frequently make calls to other integrated services. Using mock service integrations 
with [Step Functions Local](https://docs.aws.amazon.com/step-functions/latest/dg/sfn-local.html) eliminates 
the need to perform a build and deploy to the cloud between workflow modifications, enabling rapid functional 
testing without affecting cloud resources. Testing is conducted in a self-contained local environment using 
defined mocked responses of AWS service integrations. The mocked responses can be combined into test case 
scenarios to validate workflow control and data flow definitions. 

## System Under Test
The system under test in this pattern is a sales lead generation application implemented using a Step Functions workflow. 
The system contains multiple service integrations including AWS Lambda, Amazon Comprehend, and Amazon DynamoDB.

![Step Functions Workflow](images/stepfunctions_local_test.png)

## Description
Step Functions Local allows developers to define mocked outputs from AWS service integrations. This application contains
a test suite that shows several examples of [mocked service integrations](https://docs.aws.amazon.com/step-functions/latest/dg/sfn-local-test-sm-exec.html). 
Mocks can have multiple cases, testing both success and failure scenarios. When using mocked service integrations, developers 
should create an adequate amount of success and failure cases to thoroughly test all branches of their business logic prior 
to deploying to production. 

## Limitations
Local tests with mocked responses do not test cloud specific topics such as IAM policies and service configurations.
We advise developers to test their workflows in the cloud for complete coverage across services.

## How to test
Follow the instructions contained in this [sample application](https://github.com/aws-samples/aws-stepfunctions-examples/tree/main/sam/demo-local-testing-using-java) 
to see the test code written using JUnit and Spock.