[![python: 3.9](https://img.shields.io/badge/Python-3.9-green)](https://img.shields.io/badge/Python-3.9-green)
[![AWS: Lambda](https://img.shields.io/badge/AWS-Lambda-orange)](https://img.shields.io/badge/AWS-Lambda-orange)
[![test: local](https://img.shields.io/badge/Test-Local-red)](https://img.shields.io/badge/Test-Local-red)

# Local Testing: AWS Lambda Hello World

## Introduction

This project demonstrates how to test AWS Lambda functions locally using the SAM CLI. It provides a simple Hello World example that can be tested without requiring actual AWS infrastructure.

---

## Contents
- [Local Testing: AWS Lambda Hello World](#local-testing-aws-lambda-hello-world)
  - [Introduction](#introduction)
  - [Contents](#contents)
  - [Architecture Overview](#architecture-overview)
  - [Project Structure](#project-structure)
  - [Prerequisites](#prerequisites)
  - [Local Testing](#local-testing)
  - [Understanding the Output](#understanding-the-output)
  - [Additional Resources](#additional-resources)

---

## Architecture Overview
<p align="center">
  <img src="img/lambda-sam-helloworld.png" alt="AWS Lambda Hello World" width="300"/>
</p>

Components:
- Python Lambda function
- SAM CLI for local execution
- Test event for invocation

---

## Project Structure


```
├── lambda-sam-helloworld               _# folder containing necessary code and template for Hello World Lambda_
│   ├── events                          _# folder containing json files for Hello World Lambda input events_
│   ├── img/lambda-sam-helloworld.png   _# Architecture diagram_
│   ├── lambda_helloworld_src           _# folder containing code Hello World Lambda function_
│   ├── README.md                       _# instructions file_
│   └── template.yaml                   _# sam yaml template file for necessary components test_
```

---

## Prerequisites
- AWS SAM CLI
- Python 3.9
- Docker
- Basic understanding of AWS Lambda

---

## Local Testing

1. Navigate to project directory:
```sh
cd lambda-sam-helloworld
```

2. Run the Lambda function locally:
```sh
sam local invoke LambdaHelloWorld \
    --event events/lambda-helloworld-event.json
```

Expected response:
```json
{
    "statusCode": 200,
    "body": "{\"message\": \"Hello World! This is local Run!\"}"
}
```

---

## Understanding the Output

The local invocation provides detailed execution information:
- Request ID tracking
- Initialization duration
- Execution duration
- Memory usage
- Container information

Sample output details:
```
START RequestId: 7a563ee5-369d-4d7f-bcf8-c3cac3cac68f Version: $LATEST
END RequestId: da370caa-cd29-4d9b-abf9-e81ef7f6f769
REPORT RequestId: da370caa-cd29-4d9b-abf9-e81ef7f6f769
Init Duration: 0.03 ms
Duration: 44.43 ms
Billed Duration: 45 ms
Memory Size: 128 MB
Max Memory Used: 128 MB
```

---

## Additional Resources
- [SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-command-reference.html)
- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
- [SAM Local Lambda Testing Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-invoke.html)

[Top](#contents)

