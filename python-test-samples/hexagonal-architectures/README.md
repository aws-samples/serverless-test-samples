[![python: 3.9](https://img.shields.io/badge/Python-3.9-green)](https://img.shields.io/badge/Python-3.9-green)
[![AWS: DynamoDB](https://img.shields.io/badge/AWS-DynamoDB-blueviolet)](https://img.shields.io/badge/AWS-DynamoDB-blueviolet)
[![test: unit](https://img.shields.io/badge/Test-Unit-blue)](https://img.shields.io/badge/Test-Unit-blue)
[![test: integration](https://img.shields.io/badge/Test-Integration-yellow)](https://img.shields.io/badge/Test-Integration-yellow)

# Python: Hexagonal Architecture Example

## Introduction
Hexagonal architecture is a pattern used for encapsulating domain logic and decoupling it from other implementation details, such as infrastructure or client requests. You can use these types of architectures to improve how to organize and test your Lambda functions.

System Under Test (SUT)

The SUT in this pattern is a Lambda function that is organized using a hexagonal architecture. You can read this [blog post](https://aws.amazon.com/blogs/compute/developing-evolutionary-architecture-with-aws-lambda/) to learn more about these types of architectures. The example in this test pattern receives a request via API Gateway and makes calls out to other AWS cloud services like DynamoDB.

The project uses the [AWS Serverless Application Model](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) (SAM) CLI for configuration, testing and deployment. 

---

## Contents
- [Python: Hexagonal Architecture Example](#python-hexagonal-architecture-example)
  - [Introduction](#introduction)
  - [Contents](#contents)
  - [Key Files in the Project](#key-files-in-the-project)
  - [Sample project description](#sample-project-description)
    - [Terms:](#terms)
    - [Application Description](#application-description)
  - [Testing Data Considerations](#testing-data-considerations)
  - [Run the Unit Test](#run-the-unit-test)
  - [Run the Integration Test](#run-the-integration-test)
---

## Key Files in the Project
  - [app.py](src/app.py) - Lambda handler code to test
  - [template.yaml](template.yaml) - SAM script for deployment
  - [mock_test.py](tests/unit/mock_test.py) - Unit test using mocks
  - [test_api_gateway.py](tests/integration/test_api_gateway.py) - Integration tests on a live stack
  
[Top](#contents)

---

## Sample project description

Hexagonal Architecture:
Hexagonal architecture is also known as the ports and adapters architecture. It is an architectural pattern used for encapsulating domain logic and decoupling it from other implementation details, such as infrastructure or client requests. 

In Lambda functions, hexagonal architecture can help you implement new business requirements and improve the agility of a workload. This approach can help create separation of concerns and separate the domain logic from the infrastructure. For development teams, it can also simplify the implementation of new features and parallelize the work across different developers.

[Diagram](img/hexagonal-architecture-diagram.png)

### Terms:
1. Domain logic: Represents the task that the application should perform, abstracting any interaction with the external world.
2. Ports: Provide a way for the primary actors (on the left) to interact with the application, via the domain logic. The domain logic also uses ports for interacting with secondary actors (on the right) when needed.
3. Adapters: A design pattern for transforming one interface into another interface. They wrap the logic for interacting with a primary or secondary actor.
4. Primary actors: Users of the system such as a webhook, a UI request, or a test script.
5. Secondary actors: used by the application, these services are either a Repository (for example, a database) or a Recipient (such as a message queue).

### Application Description
The example application is a backend web service built using Amazon API Gateway, AWS Lambda, and Amazon DynamoDB. Business logic in the domain layer should be tested with unit tests. Responses from secondary actors via ports should be mocked during unit testing to speed up test execution. 

Adapter and port code can be tested in the cloud by deploying primary and secondary actors such as an API Gateway and a DynamoDB table. The test code will create an HTTP client that will send requests to the deployed API Gateway endpoint. The endpoint will invoke the primary actor, test resource configuration, IAM permissions, authorizers, internal business logic, and secondary actors of the SUT.

This project consists of an [API Gateway](https://aws.amazon.com/api-gateway/), a single [AWS Lambda](https://aws.amazon.com/lambda) function, and 2 [Amazon DynamoDB](https://aws.amazon.com/dynamodb) tables.

The two DynamoDB tables are meant to track Stock ID's and prices in EUR (Euros) and Euro Currency Conversion rates.

[Top](#contents)

---

## Testing Data Considerations

Data persistence brings additional testing considerations.

First, the data stores must be pre-populated with data to test certain functionality.  In our example, we need a valid stock and valid currency conversion data to test our function.  Therefore, we will add data to the data stores prior to running the tests.  This data seeding operation is performed in the test setup.  

Second, the data store will be populated as a side-effect of our testing.  In our example, stock and currency conversion data will be populated in our DynamoDB tables. To prevent unintended side-effects, we will clean-up data generated during the test execution.  This data cleaning operation is performed in the test tear-down.

[Top](#contents)

---

## Run the Unit Test
[mock_test.py](tests/unit/mock_test.py) 

In the [unit test](tests/unit/mock_test.py), all references and calls to the DynamoDB service [are mocked on line 18](tests/unit/mock_test.py#L20).

The unit test establishes the STOCKS_DB_TABLE and CURRENCIES_DB_TABLE environment
variables that the Lambda function uses to reference the DynamoDB tables. STOCKS_DB_TABLE and CURRENCIES_DB_TABLE are defined in the [setUp method of test class in mock_test.py](tests/unit/mock_test.py#L37-38).   

In a unit test, you must create a mocked version of the DynamoDB table.  The example approach in the [setUp method of test class in mock_test.py](tests/unit/mock_test.py#L43-50) reads in the DynamoDB table schema directly the [SAM Template](template.yaml) so that the definition is maintained in one place.  This simple technique works if there are no intrinsics (like !If or !Ref) in the resource properties for KeySchema, AttributeDefinitions, & BillingMode.  Once the mocked table is created, test data is populated.

With the mocked DynamoDB table created and the STOCKS_DB_TABLE and CURRENCIES_DB_TABLE set to the mocked table names, the Lambda function will use the mocked DynamoDB tables when executing.

The [unit test tear-down](tests/unit/mock_test.py#L61-66) removes the mocked DynamoDB tables and clears the STOCKS_DB_TABLE and CURRENCIES_DB_TABLE environment variables.

To run the unit test, execute the following
```shell
# Create and Activate a Python Virtual Environment
# One-time setup
hexagonal-architectures$ pip3 install virtualenv
hexagonal-architectures$ python3 -m venv venv
hexagonal-architectures$ source ./venv/bin/activate

# install dependencies
hexagonal-architectures$ pip3 install -r tests/requirements.txt

# run unit tests with mocks
hexagonal-architectures$ python3 -m coverage run -m pytest
```

[Top](#contents)

---

## Run the Integration Test

(Coming Soon)

[test_api_gateway.py](tests/integration/test_api_gateway.py) 

For integration tests, the full stack is deployed before testing:
```shell
hexagonal-architectures$ sam build
hexagonal-architectures$ sam deploy --guided
```
 
The [integration test](tests/integration/test_api_gateway.py) setup determines both the [API endpoint](tests/integration/test_api_gateway.py#L50-53) and the name of the [DynamoDB table](tests/integration/test_api_gateway.py#L56-58) in the stack.  

The integration test then [populates data into the DynamoDB table](tests/integration/test_api_gateway.py#L66-70).

The [integration test tear-down](tests/integration/test_api_gateway.py#L73-87) removes the seed data, as well as data generated during the test.

To run the integration test, create the environment variable "AWS_SAM_STACK_NAME" with the name of the test stack, and execute the test.

```shell
# Set the environment variables AWS_SAM_STACK_NAME and (optionally)AWS_DEFAULT_REGION 
# to match the name of the stack and the region where you will test

hexagonal-architectures$  AWS_SAM_STACK_NAME=<stack-name> AWS_DEFAULT_REGION=<region_name> python -m pytest -s tests/integration -v
```

[Top](#contents)

---