[![python: 3.10](https://img.shields.io/badge/Python-3.10-green)](https://img.shields.io/badge/Python-3.10-green)
[![AWS: API Gateway](https://img.shields.io/badge/AWS-API%20Gateway-blue)](https://img.shields.io/badge/AWS-API%20Gateway-blue)
[![AWS: Lambda](https://img.shields.io/badge/AWS-Lambda-orange)](https://img.shields.io/badge/AWS-Lambda-orange)
[![test: local](https://img.shields.io/badge/Test-Local-red)](https://img.shields.io/badge/Test-Local-red)

# Local: Amazon API Gateway Mock Testing

## Introduction

This project demonstrates how to test AWS API Gateway endpoints locally using SAM CLI. It showcases a simple mock implementation using Python 3.10 that returns predefined responses without requiring AWS credentials or external dependencies, making it ideal for rapid development and testing cycles.

---

## Contents

- [Local: Amazon API Gateway Mock Testing](#local-amazon-api-gateway-mock-testing)
  - [Introduction](#introduction)
  - [Contents](#contents)
  - [Architecture Overview](#architecture-overview)
  - [Project Structure](#project-structure)
  - [Prerequisites](#prerequisites)
  - [Test Scenarios](#test-scenarios)
  - [About the Test Process](#about-the-test-process)
  - [Testing Workflows](#testing-workflows)
  - [API Documentation](#api-documentation)
  - [Additional Resources](#additional-resources)

---

## Architecture Overview

<p align="center">
  <img src="img/apigw-mock-local.png" alt="API Gateway Mock Testing" width="300"/>
</p>

Components:

- API Gateway Local emulator via SAM CLI
- Python Lambda function returning JSON mock responses
- Testcontainers for container management
- PyTest for automated testing

---

## Project Structure
```
├── events                                      _# folder containing json events files_
├── img/apigw-mock-local.png                    _# visual architecture diagram_
├── lambda_mock_src/app.py                      _# Python Lambda function source code_
├── tests/
│   ├── unit/src/test_apigateway_local.py       _# python PyTest test definition_
│   └── requirements.txt                        _# pip requirements dependencies file_
├── template.yaml                               _# SAM template defining API Gateway and Lambda resources_
└── README.md                                   _# instructions file_
```
---

## Prerequisites

- Docker
- AWS SAM CLI
- Python 3.10 or newer
- curl (for API testing)
- Basic understanding of SAM, API Gateway and Lambda

---

## Test Scenarios

### 1. Mock Response Validation

- Tests the basic mock endpoint functionality
- Verifies that the API Gateway correctly routes requests to the Lambda function
- Validates the JSON response format and content
- Ensures proper HTTP status codes are returned

### 2. Local API Gateway Behavior

- Tests the local emulation of API Gateway routing
- Verifies that the `/MOCK` endpoint is accessible via GET method
- Validates that the Lambda integration works correctly in local environment

### 3. PyTest Integration Tests (end to end python test)

- **Basic API Gateway Test**: Validates API Gateway routing and Lambda integration
- **Response Format Validation**: Tests proper JSON response structure
- **Error Handling Test**: Validates behavior with invalid requests and methods
- **Performance Metrics**: Measures API response times and consistency
- **Concurrent Request Test**: Tests API behavior under concurrent load
- **Input Validation**: Tests API with various input scenarios

---

## About the Test Process

The test process leverages SAM CLI to provide local emulation of AWS services:

1. **SAM Local Setup**: SAM CLI starts a local API Gateway emulator that listens on port 3000 by default.

2. **Lambda Function Loading**: The local emulator loads the Python Lambda function code from `lambda_mock_src/app.py` and creates a containerized runtime environment using Python 3.10.

3. **API Route Mapping**: Based on the `template.yaml` configuration, SAM maps the `/MOCK` path with GET method to the Lambda function.

4. **Request Processing**: When a request is made to `http://127.0.0.1:3000/MOCK`, the local API Gateway:
   - Receives the HTTP request
   - Routes it to the appropriate Lambda function
   - Executes the Python function in a Docker container
   - Returns the response to the client

5. **Response Validation**: Tests verify that the mock response is correctly formatted and contains the expected content.

---

## Testing Workflows

### Setup Docker Environment

> Make sure Docker engine is running before running the tests.

```shell
apigw-mock-local$ docker version
Client: Docker Engine - Community
 Version:           24.0.6
 API version:       1.43
(...)
```

### Run the Unit Test - End to end python test

> Start the API Gateway emulator in a separate terminal:

```shell
apigw-mock-local$
sam local start-api --port 3000 --docker-network host &
```

> Set up the python environment:

```shell
apigw-mock-local$ cd tests
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Run the Unit Tests

```shell
apigw-mock-local/tests$
python3 -m pytest -s unit/src/test_apigateway_local.py
```

Expected output:

```shell
========================================================== test session starts========================================================== 
platform linux -- Python 3.10.12, pytest-8.4.1, pluggy-1.6.0
rootdir: /home/ubuntu/environment/python-test-samples/apigw-mock-local/tests
plugins: timeout-2.4.0, xdist-3.8.0
collected 9 items                                                                              
unit/src/test_apigateway_local.py SAM Local API Gateway is running on port 3000
API Gateway endpoint is responding correctly
API Gateway response: {'StatusCode': 200, 'Response': 'This is mock response', 'ResponseTime': 496ms}
.API Gateway response format validation passed - all headers and format requirements met
.Error handling test passed: Invalid endpoint returned status 403
Error handling test passed: Wrong HTTP method returned status 403
Error handling test passed: Unsupported HTTP method PUT returned status 403
Error handling test passed: Unsupported HTTP method DELETE returned status 403
API Gateway error handling test passed - all error scenarios handled appropriately
.Performance metrics:
  Average: 490ms
  Min: 484ms
  Max: 496ms
  Consistency: All responses within acceptable range
Performance test completed: avg=490ms, min=484ms, max=496ms
.Concurrent requests test passed
Results: Success_Rate=100.0%, Avg_Response_Time=1642ms, Successful=5/5
.Input validation test 1 passed: Basic request
Input validation test 2 passed: Request with query parameters
Input validation test 3 passed: Request with custom headers
Input validation test 4 passed: Request with Accept header
Input validation test 5 passed: Combined request with params and headers
Input validation test passed - 5 scenarios handled correctly
.Server header present: Werkzeug/3.0.1 Python/3.11.3
Response headers validation passed - all required headers present and properly formatted
.Timeout test passed: Normal timeout - 478ms
Timeout test passed: Standard timeout - 505ms
Timeout test passed: Short timeout - 484ms
Timeout handling test passed - all timeout scenarios handled correctly
.Connection resilience test passed
Results: Success_Rate=100.0%, Avg_Response_Time=499ms, Successful=10/10
.

========================================================== 9 passed in 18.17s ========================================================== 
```

#### Clean up section

> clean pyenv environment

```sh
apigw-mock-local/tests$
deactivate
rm -rf venv/
```

> stopping SAM local process:

```sh
apigw-mock-local$
ps -axuf | grep '[s]am local start-api' | awk '{print $2}' | xargs -r kill
```

#### Debug - PyTest Debugging

For more detailed debugging in pytest:

```sh
# Run with verbose output
python -m pytest -s -v unit/src/test_apigateway_local.py

# Run with debug logging
python -m pytest -s -v unit/src/test_apigateway_local.py --log-cli-level=DEBUG

# List available individual tests
python3 -m pytest unit/src/test_apigateway_local.py --collect-only

# Run a specific pytest test
python3 -m pytest -s unit/src/test_apigateway_local.py::test_api_basic_mock_response -v
```

---

### Run the Local API Testing

> Start the API Gateway emulator:

```shell
apigw-mock-local$
sam local start-api --port 3000 --docker-network host &
```

Expected output:
```shell
apigw-mock-local$
Mounting LambdaMockFunction at http://127.0.0.1:3000/MOCK [GET]

You can now browse to the above endpoints to invoke your functions. You do not need to restart/reload SAM CLI while working on your functions, changes will be reflected instantly/automatically. You only need to restart SAM CLI if you update your AWS SAM template
2024-08-05 10:30:15  * Running on http://127.0.0.1:3000/ (Press CTRL+C to quit)
```

#### Test the Mock Endpoint

```shell
apigw-mock-local$
curl -X GET http://127.0.0.1:3000/MOCK
```

Expected response:
```json
"This is mock response"
```

#### Test with Verbose Output

```shell
apigw-mock-local$
curl -v -X GET http://127.0.0.1:3000/MOCK
```

Expected verbose output:
```shell
*   Trying 127.0.0.1:3000...
* Connected to 127.0.0.1 (127.0.0.1) port 3000 (#0)
> GET /MOCK HTTP/1.1
> Host: 127.0.0.1:3000
> User-Agent: curl/8.0.1
> Accept: */*
> 
< HTTP/1.1 200 OK
< Content-Type: application/json
< Content-Length: 22
< Server: Werkzeug/2.3.6 Python/3.9.18
< Date: Mon, 05 Aug 2024 14:30:15 GMT
< 
"This is mock response"
```

#### Test Invalid Endpoints

```shell
# Test non-existent endpoint
apigw-mock-local$
curl -X GET http://127.0.0.1:3000/INVALID

# Test wrong HTTP method
curl -X POST http://127.0.0.1:3000/MOCK
```

#### Clean up section

> Stop SAM local process:

```sh
apigw-mock-local$
ps -axuf | grep '[s]am local start-api' | awk '{print $2}' | xargs -r kill
```

---

### Fast local development for API Gateway

#### Manual Lambda Function Testing

You can test the Python Lambda function directly without API Gateway:

#### Test Lambda function directly

```sh
# Test Python Lambda function locally
apigw-mock-local$
sam local invoke LambdaMockFunction --event events/test-event.json
```

#### Debug API Gateway Routes

```sh
# List all available endpoints
apigw-mock-local$
sam local start-api --port 3000 --docker-network host --debug &

# Check template syntax
apigw-mock-local$
sam validate --lint

# Generate sample events for testing
apigw-mock-local$
sam local generate-event apigateway aws-proxy > events/sample-event.json

# Build the application (Python dependencies)
apigw-mock-local$
sam build
```

---

## API Documentation

### Endpoints

| Endpoint | Method | Response Type | Status Code | Description |
|----------|---------|---------------|-------------|-------------|
| `/MOCK` | GET | JSON String | 200 | Returns a simple mock response message |

### Response Examples

**Successful Response (200):**
```json
"This is mock response"
```

**Invalid Endpoint (403):**
```json
{
  "message": "Missing Authentication Token"
}
```

### Request/Response Flow

1. **Request**: `GET /MOCK`
2. **API Gateway Processing**: Routes request to Python Lambda function
3. **Lambda Execution**: Python function returns mock response with 200 status code
4. **Response**: JSON string containing mock message

---

## Additional Resources

- [AWS SAM CLI Installation Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
- [SAM Local API Testing Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-start-api.html)
- [AWS API Gateway Developer Guide](https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html)
- [AWS Lambda Python Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)
- [Python 3.10 Runtime Guide](https://docs.aws.amazon.com/lambda/latest/dg/python-runtime.html)
- [SAM Template Specification](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-specification.html)
- [Local Testing with SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-invoke.html)

[Top](#contents)