[![python: 3.9](https://img.shields.io/badge/Python-3.9-green)](https://img.shields.io/badge/Python-3.9-green)
[![AWS: SQS](https://img.shields.io/badge/AWS-SQS-blueviolet)](https://img.shields.io/badge/AWS-SQS-blueviolet)
[![test: integration](https://img.shields.io/badge/Test-Integration-yellow)](https://img.shields.io/badge/Test-Integration-yellow)

# Python: Amazon Api Gateway, AWS Lambda, Amazon SQS Example

## Introduction
This project contains automated test sample code samples for serverless applications written in Python. The project demonstrates several techniques for executing tests in the cloud specifically when interacting with the AWS Lambda service. Based on current tooling, we recommend customers **focus on testing in the cloud** as much as possible. 

The project uses the [AWS Serverless Application Model](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) (SAM) CLI for configuration, testing and deployment. 

---

## Contents
- [Python: Amazon Api Gateway, AWS Lambda, Amazon SQS Example](#python-amazon-api-gateway-aws-lambda-amazon-dynamodb-example)
  - [Introduction](#introduction)
  - [Contents](#contents)
  - [Key Files in the Project](#key-files-in-the-project)
  - [Sample project description](#sample-project-description)
  - [Testing Data Considerations](#testing-data-considerations)
  - [Run the Unit Test](#run-the-unit-test)
---

## Key Files in the Project
  - [process_input_queue.py](src/process_input_queue/process_input_queue.py) - Lambda handler code to read from input SQS queue, do some processing, and enqueue the processing results into the output SQS queue
  - [check_output_queue.py](src/check_output_queue/check_output_queue.py) - Lambda handler code to read from output SQS queue the result of the processing
  - [template.yaml](template.yaml) - SAM script for deployment
  - [test_api_gateway.py](tests/integration/test_api_gateway.py) - Integration test written in Python on a live stack deployed on AWS
  - [client.sh](client.sh) - Simple test client that uses to run from command line (utilizes CURL) for integration tests on a live stack deployed on AWS
  
[Top](#contents)

---

## Sample project description

The sample project allows a user to call an API endpoint (using /inbox) and generate a custom "test/hello" message. The user can also track the result of the processing of it in the cloud (using /outbox). The following diagram demonstatred the architecture and flow. The following diagram has been created using the [AWS Application Composer](https://aws.amazon.com/application-composer/), which can help you visually design and build serverless applications quickly.

![Event Sequence](img/architecture.png)

This project consists of an [API Gateway](https://aws.amazon.com/api-gateway/), two [AWS Lambda](https://aws.amazon.com/lambda) functions, and two [Amazon SQS](https://aws.amazon.com/sqs) standart queues which are using 2 DLQ queues accordinally for error handling.

The Sequence is (corresponding steps 1-7  on the diagram): 

1. User is using the test client to invoke an API call (POST /inbox) to send a message/job/test to be later on processed in the backend by the ProcessInputQueue lambda function.
2. API GW is sending the message payload into the InputQueue.
3. InputQueue is triggering the ProcessInputQueue lambda function to process the message/job/test in the queue. this is where the lambda can be enhanced to do further processing/testing as needed by you. It's up to the user of this sample to decide what this lambda shuold eventualy do, as it can be extended and adapted to the testing needs. 
4. When the ProcessInputQueue lambda finished its processing, it sends the testing result to the OutputQueue (if needed - please adapt the result JSON/Message). The result will be kept in the queue until consumed by the User.
5. User is using the test client to invoke an API call (GET /outbox) to receive the testing result/message of the test it issued on step 1.
6. API GW is triggering the CheckOutputQueue lambda function to recieve the message from the OutputQueue.
7. CheckOutputQueue lambda function is receiving the the message from the OutputQueue and delivers it back to the test client via the API GW.



[Top](#contents)

---

## Testing Data Considerations

Data persistence brings additional testing considerations.

First, the data store must be pre-populated with data to test certain functionality.  In our example, we need a valid `id` to retrieve a name to test our function.  Therefore, we will add data to the data stores prior to running the tests.  This data seeding operation is performed in the test setup.  

Second, the data store will be populated as a side-effect of our testing.  In our example, items of recorded "Hello" messages will be populated in our DynamoDB table.  To prevent unintended side-effects, we will clean-up data generated during the test execution.  This data cleaning operation is performed in the test tear-down. 

Third, any identifying values should be unique to the specific test.  This will prevent 
collisions between tests should there be an issue with tear-down.  Each test can define
a unique postfix to prevent the issues.

[Top](#contents)

---

## Run the Unit Test
[mock_test.py](tests/unit/mock_test.py) 

In the [unit test](tests/unit/mock_test.py), all references and calls to the DynamoDB service [are mocked on line 18](tests/unit/mock_test.py#L20).

The unit test establishes the DYNAMODB_TABLE_NAME environment
variable that the Lambda function uses to reference the DynamoDB table.  DYNAMODB_TABLE_NAME is definied in the [setUp method of test class in mock_test.py](tests/unit/mock_test.py#L37-38).   


In a unit test, you must create a mocked version of the DynamoDB table.  The example approach in the [setUp method of test class in mock_test.py](tests/unit/mock_test.py#L43-50) reads in the DynamoDB table schema directly the [SAM Template](template.yaml) so that the definition is maintained in one place.  This simple technique works if there are no intrinsics (like !If or !Ref) in the resource properties for KeySchema, AttributeDefinitions, & BillingMode.  Once the mocked table is created, test data is populated.

With the mocked DynamoDB table created and the DYNAMODB_TABLE_NAME set to the mocked table name, the Lambda function will use the mocked DynamoDB table when executing.

The [unit test tear-down](tests/unit/mock_test.py#L61-66) removes the mocked DynamoDB table and clears the DYNAMODB_TABLE_NAME environment variable.

To run the unit test, execute the following
```shell
# Create and Activate a Python Virtual Environment
# One-time setup
apigw-lambda-dynamodb$ pip3 install virtualenv
apigw-lambda-dynamodb$ python3 -m venv venv
apigw-lambda-dynamodb$ source ./venv/bin/activate

# install dependencies
apigw-lambda-dynamodb$ pip3 install -r tests/requirements.txt

# run unit tests with mocks
apigw-lambda-dynamodb$ python3 -m pytest -s tests/unit  -v
```

[Top](#contents)

---

## Run the Integration Test
[test_api_gateway.py](tests/integration/test_api_gateway.py) 

For integration tests, the full stack is deployed before testing:
```shell
apigw-lambda-dynamodb$ sam build
apigw-lambda-dynamodb$ sam deploy --guided
```
 
The [integration test](tests/integration/test_api_gateway.py) setup determines both the [API endpoint](tests/integration/test_api_gateway.py#L50-53) and the name of the [DynamoDB table](tests/integration/test_api_gateway.py#L56-58) in the stack.  

The integration test then [populates data into the DyanamoDB table](tests/integration/test_api_gateway.py#L66-70).

The [integration test tear-down](tests/integration/test_api_gateway.py#L73-87) removes the seed data, as well as data generated during the test.

To run the integration test, create the environment variable "AWS_SAM_STACK_NAME" with the name of the test stack, and execute the test.

```shell
# Set the environment variables AWS_SAM_STACK_NAME and (optionally)AWS_DEFAULT_REGION 
# to match the name of the stack and the region where you will test

apigw-lambda-dynamodb$  AWS_SAM_STACK_NAME=<stack-name> AWS_DEFAULT_REGION=<region_name> python -m pytest -s tests/integration -v
```


[Top](#contents)

---

