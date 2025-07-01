[![python: 3.10](https://img.shields.io/badge/Python-3.10-green)](https://img.shields.io/badge/Python-3.10-green)
[![AWS: Step Functions](https://img.shields.io/badge/AWS-Step%20Functions-orange)](https://img.shields.io/badge/AWS-Step%20Functions-orange)
[![Language: ASL](https://img.shields.io/badge/Language-ASL-blue)](https://img.shields.io/badge/Language-ASL-blue)
[![test: pytest](https://img.shields.io/badge/Test-Pytest-red)](https://img.shields.io/badge/Test-Pytest-red)
[![test: local](https://img.shields.io/badge/Test-Local-red)](https://img.shields.io/badge/Test-Local-red)

# AWS Step Functions: Hello World with PyTest

## Introduction

This project demonstrates how to test AWS Step Functions state machines locally using Docker and PyTest. It focuses on a simple "Hello World" state machine with a Pass state, showing how to create and validate automated tests for AWS Step Functions locally.


---

## Contents
- [AWS Step Functions: Hello World with PyTest](#aws-step-functions-hello-world-with-pytest)
  - [Introduction](#introduction)
  - [Contents](#contents)
  - [Architecture Overview](#architecture-overview)
  - [Project Structure](#project-structure)
  - [Prerequisites](#prerequisites)
  - [Test Scenarios](#test-scenarios)
  - [About the Test Process](#about-the-test-process)
  - [Testing Workflows](#testing-workflows)
  - [Additional Resources](#additional-resources)

---

## Architecture Overview
<p align="center">
  <img src="img/stepfunctions-helloworld.png" alt="Hello World Step Functions" width="300"/>
</p>

Components:
- Simple Step Functions state machine with a Pass state
- Testcontainers for container management
- PyTest for automated testing
- AWS Step Functions Local for local execution

<p align="center">
  <img src="img/stepfunctions-helloworld-states.png" alt="Hello World Step Functions - States" width="300"/>
</p>

---

## Project Structure
```
├── img/
│   ├── stepfunctions-helloworld-states.png     _# Step Functions state flow_
│   └── stepfunctions-mock.png                  _# visual architecture diagram_
├── statemachine/                              
│   ├── local_testing.asl.json                  _# json file containing "Hello World" state machine definition_
│   └── test/valid_input.json                   _# json file containing "Hello World" state machine input_
├── tests/
│   ├── unit/src/test_step_functions_local.py   _# python PyTest test definition_
│   ├── aws-stepfunctions-local-credentials.txt _# Step Functions Docker image environment vars_
│   └── requirements.txt                        _# pip requirments dependencies file_
└── README.md                                   _# instructions file_
```

---

## Prerequisites
- Docker
- AWS cli (debugging)
- Python 3.10 or newer
- Basic understanding of Step Functions
- Basic understanding of Amazon States Language (ASL)

---

## Test Scenarios (end to end python test)

### 1. Hello World
- Tests the happy path where a single state in step funtions succeed on the first attempt
- Used to validate the basic functionality of the state machine

---

## About the Test Process

The test process leverages PyTest fixtures to manage the lifecycle of the Step Functions Local container and the state machine:

1. **Container Setup**: The `fixture_container` fixture downloads and starts the `amazon/aws-stepfunctions-local` container.

2. **State Machine Creation**: The `fixture_sfn_client` fixture creates a Boto3 client for Step Functions and creates the state machine using the definition from `local_testing.asl.json`.

3. **Test Execution**: When the test runs, it calls `execute_stepfunction` to start an execution of the state machine and monitor it until completion.

4. **Validation**: The test verifies that:
   - The execution completed successfully
   - The HelloWorld state was properly exited

5. **Cleanup**: After the test completes, the container is automatically shut down by the finalizer added in the `fixture_container`.

---

## Testing Workflows

### Setup Docker Environment

> Make sure Docker engine is running before running the tests.

```shell
step-functions-local-lambda$ docker version
Client: Docker Engine - Community
 Version:           24.0.6
 API version:       1.43
(...)
```

### Run the Unit Test - End to end python test

> Set up the python environment

``` shell
step-functions-local-helloworld$ cd tests
export AWS_ACCESS_KEY_ID='DUMMYIDEXAMPLE'
export AWS_SECRET_ACCESS_KEY='DUMMYEXAMPLEKEY'
export AWS_REGION='us-east-1'
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Run the unit tests

``` shell
step-functions-local-helloworld/tests$
python3 -m pytest -s unit/src/test_step_functions_local.py
```

Expected output:
``` shell
step-functions-local-helloworld/tests$ python3 -m pytest -s unit/src/test_step_functions_local.py
========================================================== test session starts ==========================================================
platform linux -- Python 3.10.12, pytest-8.4.1, pluggy-1.6.0
rootdir: /home/ubuntu/environment/serverless-test-samples-approach-2-pytest-distributed_Try3/step-functions-local-helloworld--OK/tests
collected 1 item                                                                                                                                                                                                                                         

unit/src/test_step_functions_local.py Pulling image testcontainers/ryuk:0.8.1
Container started: ecdd9649b97d
Waiting for container <Container: ecdd9649b97d> with image testcontainers/ryuk:0.8.1 to be ready ...
Pulling image amazon/aws-stepfunctions-local
Container started: d1bd33969e6b
Waiting for container <Container: d1bd33969e6b> with image amazon/aws-stepfunctions-local to be ready ...
.

========================================================== 1 passed in 10.57s ==========================================================
(
```

#### Clean up section

> clean pyenv environment

```sh
step-functions-local-helloworld/tests$
deactivate
rm -rf venv/
```

> unsetting variables

```sh
unset AWS_ACCESS_KEY_ID='DUMMYIDEXAMPLE'
unset AWS_SECRET_ACCESS_KEY='DUMMYEXAMPLEKEY'
unset AWS_REGION='us-east-1'
```

> cleanning docker

```sh
docker ps --filter "ancestor=amazon/aws-stepfunctions-local" -q | xargs -r docker kill
docker rmi amazon/aws-stepfunctions-local
```

#### Debug - PyTest Debugging

For more detailed debugging in pytest:

```sh
# Run with verbose output
python -m pytest -s -v unit/src/test_step_functions_local.py

# Run with debug logging
python -m pytest -s -v unit/src/test_step_functions_local.py --log-cli-level=DEBUG
```

---

### Fast local development for Step Functions

#### AWS CLI Commands for Manual Verification

If you need to manually verify the state machine or execution details, you can use these commands:

#### Configure environment variables:

```sh
step-functions-local-helloworld/tests$
export AWS_ACCESS_KEY_ID='DUMMYIDEXAMPLE'
export AWS_SECRET_ACCESS_KEY='DUMMYEXAMPLEKEY'
export AWS_REGION='us-east-1'
```

#### Set up state machine machine manually

```sh
# Runing step functions docker image in the background
step-functions-local-helloworld/tests$
docker run -d --network host            \
    --name stepfunctions -p 8083:8083   \
    --env-file aws-stepfunctions-local-credentials.txt amazon/aws-stepfunctions-local
```

```sh
# Creating Hello World state machine
aws stepfunctions create-state-machine --endpoint-url http://localhost:8083     \
  --name "CRUDDynamoDB" --role-arn "arn:aws:iam::012345678901:role/DummyRole"   \
  --region us-east-1                                                            \
  --definition file://../statemachine/local_testing.asl.json
```

#### Debug state machine - aws cli debugging

```sh
# Get state machine ARN
aws stepfunctions list-state-machines --endpoint-url http://localhost:8083

# Check state machine definition
aws stepfunctions describe-state-machine --endpoint-url http://localhost:8083 \
    --state-machine-arn [STATE-MACHINE-ARN]

# Start state machine manually
aws stepfunctions start-execution --endpoint-url http://localhost:8083 \
  --state-machine-arn [STATE-MACHINE-ARN]

# Check execution details
aws stepfunctions describe-execution --endpoint http://localhost:8083 \
    --execution-arn [STATE-MACHINE-EXECUTION-ARN]

# Check execution history
aws stepfunctions get-execution-history --endpoint http://localhost:8083 \
    --execution-arn [STATE-MACHINE-EXECUTION-ARN]
```

---

## Additional Resources
- [Step Functions Local Guide](https://docs.aws.amazon.com/step-functions/latest/dg/sfn-local.html)
- [Amazon States Language Documentation](https://docs.aws.amazon.com/step-functions/latest/dg/concepts-amazon-states-language.html)
- [AWS Step Functions Developer Guide](https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html)
- [PyTest Documentation](https://docs.pytest.org/)
- [Testcontainers Python Documentation](https://testcontainers-python.readthedocs.io/en/latest/)

[Top](#contents)