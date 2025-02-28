[![python: 3.9](https://img.shields.io/badge/Python-3.9-green)](https://img.shields.io/badge/Python-3.9-green)
[![AWS: DynamoDB](https://img.shields.io/badge/AWS-DynamoDB-blueviolet)](https://img.shields.io/badge/AWS-DynamoDB-blueviolet)
[![AWS: Lambda](https://img.shields.io/badge/AWS-Lambda-orange)](https://img.shields.io/badge/AWS-Lambda-orange)
[![test: local](https://img.shields.io/badge/Test-Local-red)](https://img.shields.io/badge/Test-Local-red)

# Local: AWS Lambda Functions with DynamoDB

## Introduction

This project demonstrates how to test AWS Lambda functions that interact with DynamoDB locally using SAM CLI and Docker. It provides a complete example of CRUD operations through Lambda functions without requiring actual AWS infrastructure.

---

## Contents
- [Local: AWS Lambda Functions with DynamoDB](#local-aws-lambda-functions-with-dynamodb)
  - [Introduction](#introduction)
  - [Contents](#contents)
  - [Architecture Overview](#architecture-overview)
  - [Project Structure](#project-structure)
  - [Prerequisites](#prerequisites)
  - [Local Setup](#local-setup)
  - [Lambda Function Operations](#lambda-function-operations)
  - [Additional Resources](#additional-resources)

---

## Architecture Overview
<p align="center">
  <img src="img/dynamodb-crud-lambda.png" alt="AWS Lambda Functions with DynamoDB" width="300"/>
</p>

Components:
- Lambda functions implementing CRUD operations
- Local DynamoDB instance running in Docker
- SAM CLI for local Lambda execution

---

## Project Structure
```
├── dynamodb-crud-lambda                _# folder containing necessary code and template for Lambda DynamoDB CRUD operations_
│   ├── events                          _# folder containing json files for Lambda DynamoDB CRUD operations_
│   ├── img/dynamodb-crud-lambda.png    _# Architecture diagram_
│   ├── lambda_crud_src                 _# folder containing code for different CRUD Lambda functions_
│   ├── README.md                       _# instructions file_
│   └── template.yaml                   _# sam yaml template file for necessary components test_
```

---

## Prerequisites
- AWS SAM CLI
- Docker
- Python 3.9
- Basic understanding of AWS Lambda and DynamoDB

---

## Local Setup

1. Navigate to project directory:
```sh
cd dynamodb-crud-lambda
```

2. Start DynamoDB locally:
```sh
docker run --rm -d --network host -p 8000:8000 amazon/dynamodb-local
```

3. Configure environment:
```sh
export AWS_ACCESS_KEY_ID='DUMMYIDEXAMPLE'
export AWS_SECRET_ACCESS_KEY='DUMMYEXAMPLEKEY'
export REGION='eu-west-1'
```

---

## Lambda Function Operations

### Initialize DynamoDB CRUDLocalTable Table
```sh
sam local invoke CRUDLambdaInitFunction \
    --docker-network host \
    --event events/lambda-init-event.json
```

### Create initial Item
```sh
sam local invoke CRUDLambdaCreateFunction \
    --docker-network host \
    --event events/lambda-create-event.json
```

### Read Item
```sh
sam local invoke CRUDLambdaReadFunction \
    --docker-network host \
    --event events/lambda-read-event.json
```

### Update Item
```sh
sam local invoke CRUDLambdaUpdateFunction \
    --docker-network host \
    --event events/lambda-update-event.json
```

### Delete Item
```sh
sam local invoke CRUDLambdaDeleteFunction \
    --docker-network host \
    --event events/lambda-delete-event.json
```

Each operation returns a JSON response indicating success or failure, along with relevant data.

---

## Additional Resources
- [DynamoDB Local Documentation](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html)
- [SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-command-reference.html)
- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)

[Top](#contents)

---
