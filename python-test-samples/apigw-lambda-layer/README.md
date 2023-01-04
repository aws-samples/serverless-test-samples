[![python: 3.9](https://img.shields.io/badge/Python-3.9-green)](https://img.shields.io/badge/Python-3.9-green)
[![AWS: Lambda](https://img.shields.io/badge/AWS-Lambda-blueviolet)](https://img.shields.io/badge/AWS-Lambda-blueviolet)
[![test: unit](https://img.shields.io/badge/Test-Unit-blue)](https://img.shields.io/badge/Test-Unit-blue)

# Python AWS Lambda Layer Test Demonstration

## Introduction

This project expands on the [apigw-lambda](../apigw-lambda/README.md) introductory example, and adds [Lambda Layers](https://docs.aws.amazon.com/lambda/latest/dg/invocation-layers.html) to the sample Lambda function to demonstrate test approaches.

---

## Unit Test of Layers

When creating unit tests, create a separate test harnesses for each layer to test its functionality, as seen in [tests/unit/mock_test_samplecodelayer.py](tests/unit/mock_test_samplecodelayer.py).  

When running in the unit tests for the Lambda function, the layer modules are not available to the Lambda function as they would be in a deployed Lambda runtime environment.  To accomodate this in the unit test code, add the path of the layers in the unit test before importing the lambda hander, as seen on lines 9:10 of [tests/unit/mock_test_samplelambda.py](tests/unit/mock_test_samplelambda.py#L9-L10):

```python
path.append("src/sampleCodeLayer/python")
path.append("src/sampleSchemaLayer/python")
from src.sampleLambda import app
```

In the unit test for the Lambda function, the layer is patched and not re-tested, as coverage is provided in the test for the layer.  As seen in [tests/unit/mock_test_samplelambda.py](tests/unit/mock_test_samplelambda.py#L20-L21) lines 20-21, you can patch the layer and mock it's return value.

To run the unit tests:

```bash

# install dependencies
apigw-lambda-layer$ pip3 install virtualenv
apigw-lambda-layer$ python3 -m venv venv
apigw-lambda-layer$ source venv/bin/activate
apigw-lambda-layer$ pip3 install -r tests/requirements.txt

# run Lambda layer unit tests with mocks
apigw-lambda-layer$ python3 -m pytest -s tests/unit/mock_test_samplecodelayer.py -v

# run Lambda function unit tests with patched layer
apigw-lambda-layer$ python3 -m pytest -s tests/unit/mock_test_samplelambda.py -v
```

---

## Other Testing

Using Lambda layers does not affect the other tests, as the layer functionality is implicitly tested with the invocation of the Lambda function. 
Therefore, integration tests and load testing is the same as seen in [apigw-lambda](../apigw-lambda)
